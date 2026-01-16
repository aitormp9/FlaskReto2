import socket
import threading
import pickle

# Configuración del servidor
HOST = '0.0.0.0'  # Escucha a todos
PORT = 2000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

# Estado global del juego
game_state = {
    "players": {},  # Guardará {id: {'x': x, 'y': y}}
    "flag": {"x": 640, "y": 360, "estado": None}
}


def handle_client(conn, addr):
    print(f"[NUEVA CONEXIÓN] {addr}")
    while True:
        try:
            data = conn.recv(4096)
            if not data: break

            # Recibir posición del jugador
            player_data = pickle.loads(data)
            game_state["players"][addr] = player_data

            # Enviar el estado global de vuelta
            conn.sendall(pickle.dumps(game_state))
        except:
            break

    print(f"[DESCONECTADO] {addr}")
    if addr in game_state["players"]:
        del game_state["players"][addr]
    conn.close()


print("Servidor esperando conexiones...")
while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()