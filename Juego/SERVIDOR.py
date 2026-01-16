import socket
import threading
import pickle

HOST = '0.0.0.0'
PORT = 2000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

game_state = {
    "players": {},
    "flag": {"x": 640, "y": 360, "estado": None}
}

p_count = 0


def handle_client(conn, addr, player_id):
    global p_count
    # Enviamos el ID asignado al cliente
    conn.send(pickle.dumps(player_id))

    while True:
        try:
            data = conn.recv(4096)
            if not data: break

            player_data = pickle.loads(data)
            # Actualizamos el estado global con la info de este ID
            game_state["players"][player_id] = player_data

            # Respondemos con TODO el estado del juego
            conn.sendall(pickle.dumps(game_state))
        except:
            break

    # --- AL DESCONECTAR ---
    print(f"Jugador {player_id} desconectado")

    # Eliminamos al jugador del diccionario
    if player_id in game_state["players"]:
        del game_state["players"][player_id]

    # REINICIO LÓGICO:
    # Si el diccionario está vacío, reiniciamos el contador a 0
    if not game_state["players"]:
        p_count = 0
        print("Servidor vacío. Contador reseteado a 0.")

    conn.close()


print("Servidor listo y esperando en el puerto 2000...")

while True:
    conn, addr = server.accept()

    # IMPORTANTE: Solo sumamos si no hemos llegado al límite de 4
    if p_count < 4:
        p_count += 1
        print(f"Asignando ID: {p_count} a {addr}")
        threading.Thread(target=handle_client, args=(conn, addr, p_count)).start()
    else:
        print("Servidor lleno, conexión rechazada.")
        conn.close()