import socket
import threading
import pickle

# --- CONFIGURACIÓN ---
HOST = '0.0.0.0'
PORT = 2000
MAX_JUGADORES = 4

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

# Estado global del juego
game_state = {
    "players": {},
    "puntuacion": [0, 0, 0, 0],
    "rondas": [0, 0, 0, 0],
    "band_x": 640,  # Posición inicial de la bandera
    "band_y": 360
}

state_lock = threading.Lock()

def handle_client(conn, addr, player_id):
    print(f"[NUEVO] Jugador {player_id} conectado desde {addr}")

    try:
        conn.send(pickle.dumps(player_id))

        while True:
            data = conn.recv(8192)
            if not data:
                break

            datos_recibidos = pickle.loads(data)

            with state_lock:
                # 1. Actualizar posición del jugador
                game_state["players"][player_id] = {
                    "x": datos_recibidos["x"],
                    "y": datos_recibidos["y"]
                }

                # 2. Sincronizar sus puntos y rondas
                idx = player_id - 1
                game_state["puntuacion"][idx] = datos_recibidos["puntuacion"]
                game_state["rondas"][idx] = datos_recibidos["rondas"]

                # 3. NECESARIO: Actualizar posición de la bandera en el servidor
                # Guardamos la posición que nos mande el cliente que la tenga
                game_state["band_x"] = datos_recibidos.get("band_x", game_state["band_x"])
                game_state["band_y"] = datos_recibidos.get("band_y", game_state["band_y"])

                respuesta = pickle.dumps(game_state)

            conn.sendall(respuesta)

    except Exception as e:
        print(f"[ERROR] Jugador {player_id}: {e}")
    finally:
        with state_lock:
            if player_id in game_state["players"]:
                del game_state["players"][player_id]
        print(f"[DESCONECTADO] Jugador {player_id} ha salido.")
        conn.close()

print(f"Servidor iniciado en {HOST}:{PORT}. Esperando jugadores...")

while True:
    conn, addr = server.accept()
    with state_lock:
        nuevo_id = None
        for i in range(1, MAX_JUGADORES + 1):
            if i not in game_state["players"]:
                nuevo_id = i
                break

    if nuevo_id:
        with state_lock:
            game_state["players"][nuevo_id] = {"x": 0, "y": 0}
        thread = threading.Thread(target=handle_client, args=(conn, addr, nuevo_id))
        thread.start()
    else:
        conn.close()