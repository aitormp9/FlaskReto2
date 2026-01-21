import socket
import threading
import pickle

# --- CONFIGURACIÓN ---
HOST = '0.0.0.0'  # Escucha en todas las interfaces
PORT = 2000
MAX_JUGADORES = 4

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

# Estado global del juego
game_state = {
    "players": {},  # Diccionario para posiciones: {id: {"x": x, "y": y}}
    "puntuacion": [0, 0, 0, 0],  # Puntos de los jugadores 1, 2, 3 y 4
    "rondas": [0, 0, 0, 0]  # Rondas ganadas por cada uno
}

# Lock para evitar que dos hilos escriban al mismo tiempo y corrompan los datos
state_lock = threading.Lock()


def handle_client(conn, addr, player_id):
    print(f"[NUEVO] Jugador {player_id} conectado desde {addr}")

    try:
        # 1. Enviamos el ID asignado al cliente nada más conectar
        conn.send(pickle.dumps(player_id))

        while True:
            # 2. Recibimos datos del cliente (x, y, puntos, rondas)
            data = conn.recv(8192)  # Buffer aumentado para evitar cortes
            if not data:
                break

            datos_recibidos = pickle.loads(data)

            with state_lock:
                # 1. Actualizar posición (Como ya hacías)
                game_state["players"][player_id] = {
                    "x": datos_recibidos["x"],
                    "y": datos_recibidos["y"]
                }

                # 2. Actualizar puntos y rondas en la LISTA GLOBAL del servidor
                idx = player_id - 1
                game_state["puntuacion"][idx] = datos_recibidos["mi_puntuacion"]
                game_state["rondas"][idx] = datos_recibidos["mi_ronda"]

                # 3. Enviar todo el paquete de vuelta
                respuesta = pickle.dumps(game_state)
                conn.sendall(respuesta)
    except Exception as e:
        print(f"[ERROR] Jugador {player_id}: {e}")
    finally:
        # Limpieza al desconectarse
        with state_lock:
            if player_id in game_state["players"]:
                del game_state["players"][player_id]
        print(f"[DESCONECTADO] Jugador {player_id} ha salido.")
        conn.close()


print(f"Servidor iniciado en {HOST}:{PORT}. Esperando jugadores...")

while True:
    conn, addr = server.accept()

    with state_lock:
        # Buscamos el primer ID libre entre 1 y 4
        nuevo_id = None
        for i in range(1, MAX_JUGADORES + 1):
            if i not in game_state["players"]:
                nuevo_id = i
                break

    if nuevo_id:
        # Reservamos el ID temporalmente para que no se asigne a otro mientras arranca el hilo
        with state_lock:
            game_state["players"][nuevo_id] = {"x": 0, "y": 0}

        thread = threading.Thread(target=handle_client, args=(conn, addr, nuevo_id))
        thread.start()
    else:
        print(f"Conexión rechazada para {addr}: Sala llena.")
        conn.close()