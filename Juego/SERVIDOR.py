import socket
import threading
import pickle

HOST = '0.0.0.0'
PORT = 2000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

# El estado global del juego
game_state = {
    "players": {},
    "puntuacion": [0, 0, 0, 0],
    "rondas": [0, 0, 0, 0]
}


def handle_client(conn, addr, player_id):
    print(f"[NUEVA CONEXIÓN] Jugador {player_id} conectado desde {addr}")
    conn.send(pickle.dumps(player_id))

    while True:
        try:
            data = conn.recv(4096)
            if not data: break

            incoming = pickle.loads(data)

            # Actualizamos posición del jugador
            game_state["players"][player_id] = {
                "x": incoming["x"],
                "y": incoming["y"]
            }

            # El servidor confía en la actualización de puntos del cliente
            game_state["puntuacion"] = incoming["puntuacion"]
            game_state["rondas"] = incoming["rondas"]

            # Respondemos con el estado completo a todos
            conn.sendall(pickle.dumps(game_state))
        except:
            break

    print(f"[DESCONEXIÓN] Jugador {player_id} salió.")
    if player_id in game_state["players"]:
        del game_state["players"][player_id]
    conn.close()


print("Servidor escuchando en el puerto 2000...")
while True:
    conn, addr = server.accept()
    nuevo_id = 1
    while nuevo_id in game_state["players"]:
        nuevo_id += 1

    if nuevo_id <= 4:
        threading.Thread(target=handle_client, args=(conn, addr, nuevo_id)).start()
    else:
        conn.close()