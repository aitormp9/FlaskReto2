import socket
import threading
import random

# Configuración
HOST = '0.0.0.0'
PORT = 65432
posiciones_iniciales = [
    "25,25",
    "1245,25",
    "25,685",
    "1246,685"
]

# Guardamos datos de los jugadores {id: [x, y]}
posiciones_actuales = {}
clientes = {}  # {id: socket_del_cliente}


def generar_muros():
    muros = []
    # Definimos las zonas (x, y, finx, finy)
    zonas = [
        (100, 100, 540, 260),  # Zona 1
        (740, 100, 1180, 260),  # Zona 2
        (100, 460, 540, 620),  # Zona 3
        (740, 460, 1180, 620)  # Zona 4
    ]

    ancho, alto = random.randint(10, 150), random.randint(10, 200)  # Tamaño de los muros

    for zona in zonas:
        x_min, y_min, x_max, y_max = zona
        for _ in range(4):  # 4 muros por zona como en tu ejemplo
            mx = random.randint(x_min, x_max)
            my = random.randint(y_min, y_max)

            # Ajustes de borde que pediste
            if mx < 50: mx += 50
            if my < 50: my += 50
            if mx + ancho > 1180: mx = 1180 - ancho
            if my + alto > 620: my = 620 - alto

            muros.append(f"{mx},{my}")
    return "|".join(muros)


# Generamos los muros una sola vez al iniciar el servidor
DATOS_MUROS = generar_muros()

def manejar_jugador(conn, jugador_id):
    print(f"Jugador {jugador_id} conectado.")
    pos_inicial = posiciones_iniciales[jugador_id % 5]
    conn.sendall(f"START:{pos_inicial}".encode('utf-8'))

    posiciones_actuales[jugador_id] = pos_inicial
    clientes[jugador_id] = conn

    while True:
        try:
            # Recibir posición "x,y"
            data = conn.recv(1024).decode('utf-8')
            if not data: break

            # Actualizar posición del jugador en el diccionario
            posiciones_actuales[jugador_id] = data

            # Crear paquete de datos: "id:x,y|id:x,y"
            # Solo incluimos a los jugadores que han enviado su posición
            paquete = "|".join([f"{idx}:{pos}" for idx, pos in posiciones_actuales.items()])

            # Enviar a TODOS los que estén conectados actualmente
            for c_id, c_sock in list(clientes.items()):
                try:
                    c_sock.sendall(paquete.encode('utf-8'))
                except:
                    # Si falla el envío, eliminamos al cliente
                    del clientes[c_id]
                    if c_id in posiciones_actuales: del posiciones_actuales[c_id]
        except:
            break

    print(f"Jugador {jugador_id} desconectado.")
    conn.close()
    jugador_id-=1
    if jugador_id in clientes: del clientes[jugador_id]
    if jugador_id in posiciones_actuales: del posiciones_actuales[jugador_id]

#--------------------------------------------------------------------
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("Servidor listo. Puedes abrir hasta 5 ventanas de juego.")
id_contador = 0
while True:
    conn, addr = server.accept()
    # Cada vez que alguien entra, le damos un ID único
    threading.Thread(target=manejar_jugador, args=(conn, id_contador), daemon=True).start()
    id_contador += 1