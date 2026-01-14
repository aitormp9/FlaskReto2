import socket
import threading
import pickle

# --- Configuración del servidor ---
HOST = ''  # escuchar en todas las interfaces
PORT = 2000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
players = {}  # Diccionario de todos los jugadores
flag = {"x": 250, "y": 250, "estado": None}  # Posición inicial de la bandera

lock = threading.Lock()  # Para evitar conflictos al actualizar players

# --- Función para enviar el estado a todos los clientes ---
def broadcast_state():
    state = {'players': players, 'flag': flag}
    for c in clients:
        try:
            c.sendall(pickle.dumps(state))
        except:
            pass  # si un cliente está caído, lo ignoramos por ahora

# --- Manejo de cada cliente ---
def handle_client(conn, addr):
    print(f"Jugador {addr} conectado.")

    with lock:
        # Posición inicial aleatoria o predefinida
        players[addr] = {"x": 0, "y": 0}

    connected = True
    while connected:
        try:
            data = conn.recv(4096)
            if not data:
                break

            # Convertimos datos de bytes a diccionario Python
            player_data = pickle.loads(data)

            # Actualizamos la posición del jugador
            with lock:
                players[addr].update(player_data)

                # --- Lógica básica para agarrar la bandera ---
                px, py = players[addr]['x'], players[addr]['y']
                if abs(px - flag['x']) < 30 and abs(py - flag['y']) < 30:
                    flag['estado'] = addr  # jugador que tiene la bandera

            # Enviar estado actualizado a todos los clientes
            broadcast_state()

        except:
            break

    # Cliente desconectado
    print(f"Jugador {addr} desconectado.")
    with lock:
        if addr in players:
            del players[addr]
        if conn in clients:
            clients.remove(conn)
    conn.close()

# --- Función principal para aceptar clientes ---
def start():
    print("Servidor iniciado, esperando jugadores...")
    while True:
        conn, addr = server.accept()
        clients.append(conn)
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()

start()
