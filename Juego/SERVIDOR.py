import socket
import threading
import random

# Configuración
HOST = '0.0.0.0'
PORT = 65432

posiciones_iniciales = ["25,25", "1245,25", "25,685", "1246,685"]


def generar_muros():
    muros = []
    zonas = [
        (100, 100, 540, 260), (740, 100, 1180, 260),
        (100, 460, 540, 620), (740, 460, 1180, 620)
    ]

    for zona in zonas:
        x_min, y_min, x_max, y_max = zona
        for _ in range(4):
            # TAMAÑO INDIVIDUAL PARA CADA MURO
            ancho = random.randint(10, 150)
            alto = random.randint(10, 200)

            mx = random.randint(x_min, x_max)
            my = random.randint(y_min, y_max)

            # Ajustes de borde originales
            if mx < 50: mx += 50
            if my < 50: my += 50
            if mx + ancho > 1180: mx = 1180 - ancho
            if my + alto > 620: my = 620 - alto

            muros.append(f"{mx},{my},{ancho},{alto}")
    return "|".join(muros)


# Esto se ejecuta UNA VEZ cuando abres el servidor
DATOS_MUROS = generar_muros()
posiciones_actuales = {}
clientes = {}


def manejar_jugador(conn, jugador_id):
    pos_inicial = posiciones_iniciales[jugador_id % 4]
    mensaje_bienvenida = f"START:{pos_inicial}#{DATOS_MUROS}"
    conn.sendall(mensaje_bienvenida.encode('utf-8'))

    posiciones_actuales[jugador_id] = pos_inicial
    clientes[jugador_id] = conn

    while True:
        try:
            data = conn.recv(1024).decode('utf-8')
            if not data: break
            posiciones_actuales[jugador_id] = data
            paquete = "|".join([f"{idx}:{pos}" for idx, pos in posiciones_actuales.items()])
            for c_sock in list(clientes.values()):
                try:
                    c_sock.sendall(paquete.encode('utf-8'))
                except:
                    pass
        except:
            break

    if jugador_id in clientes: del clientes[jugador_id]
    if jugador_id in posiciones_actuales: del posiciones_actuales[jugador_id]
    conn.close()


if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # EVITA EL ERROR DE BIND REUTILIZANDO EL PUERTO
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print("Servidor funcionando. Muros aleatorios generados.")

    id_contador = 0
    while True:
        conn, addr = server.accept()
        threading.Thread(target=manejar_jugador, args=(conn, id_contador), daemon=True).start()
        id_contador += 1