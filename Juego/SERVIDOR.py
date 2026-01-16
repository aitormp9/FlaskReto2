import socket
import threading
import pickle

HOST = '0.0.0.0'
PORT = 2000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

game_state = {
    "players": {}  # Aquí guardaremos { 1: {"x":...}, 2: {"x":...} }
}


# --- En server.py ---
def handle_client(conn, addr, player_id):
    conn.send(pickle.dumps(player_id)) # Enviamos 1, 2, 3 o 4
    while True:
        try:
            data = conn.recv(4096)
            if not data: break
            # Guardamos exactamente en su posición
            game_state["players"][player_id] = pickle.loads(data)
            conn.sendall(pickle.dumps(game_state))
        except: break
    # Limpiar al salir
    if player_id in game_state["players"]:
        del game_state["players"][player_id]


print("Servidor iniciado...")
ids_ocupados = set()
while True:
    conn, addr = server.accept()
    # Buscar el ID más bajo disponible (1, 2, 3 o 4)
    nuevo_id = 1
    while nuevo_id in game_state["players"]:
        nuevo_id += 1

    if nuevo_id <= 4:
        threading.Thread(target=handle_client, args=(conn, addr, nuevo_id)).start()
    else:
        conn.close()