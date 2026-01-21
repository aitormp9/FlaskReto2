import socket
import threading
import pickle

HOST = '0.0.0.0'
PORT = 2000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

# Usamos un Lock para que los hilos no modifiquen el dict al mismo tiempo
state_lock = threading.Lock()

game_state = {
    "players": {},
    "puntuacion": [0, 0, 0, 0],
    "rondas": [0, 0, 0, 0]
}


def handle_client(conn, addr, player_id):
    print(f"[CONECTADO] Jugador {player_id}")
    try:
        conn.send(pickle.dumps(player_id))

        while True:
            data = conn.recv(4096)
            if not data: break

            incoming = pickle.loads(data)

            with state_lock:
                # Actualizar posición
                game_state["players"][player_id] = {
                    "x": incoming["x"],
                    "y": incoming["y"]
                }

                # REGLA DE ORO: Solo actualizamos si el valor recibido es mayor
                # al que ya tenemos (evita que un jugador resetee a los demás)
                for i in range(4):
                    if incoming["puntuacion"][i] > game_state["puntuacion"][i]:
                        game_state["puntuacion"][i] = incoming["puntuacion"][i]
                    if incoming["rondas"][i] > game_state["rondas"][i]:
                        game_state["rondas"][i] = incoming["rondas"][i]

                # Enviamos la copia actualizada
                conn.sendall(pickle.dumps(game_state))

    except Exception as e:
        print(f"[ERROR] Jugador {player_id}: {e}")
    finally:
        with state_lock:
            if player_id in game_state["players"]:
                del game_state["players"][player_id]
        conn.close()


print("Servidor iniciado en puerto 2000...")
while True:
    conn, addr = server.accept()
    # Asignar ID basado en slots libres 1-4
    with state_lock:
        nuevo_id = next((i for i in range(1, 5) if i not in game_state["players"]), None)

    if nuevo_id:
        threading.Thread(target=handle_client, args=(conn, addr, nuevo_id), daemon=True).start()
    else:
        conn.close()