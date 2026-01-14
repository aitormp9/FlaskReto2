import socket
import pickle
import threading
import time

# --- Configuración ---
HOST = '0.0.0.0'   # Escucha en todas las interfaces
PORT = 2000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print("Servidor iniciado, esperando jugadores...")

clients = []
players = {}  # Diccionario {id: {"x": , "y": }}
flag = {"x": 640, "y": 360, "estado": None}  # Posición de la bandera

lock = threading.Lock()  # Para proteger acceso concurrente a players

# --- Función para enviar estado a todos ---
def broadcast_state():
    state = {"players": players, "flag": flag}
    for c in clients:
        try:
            c.sendall(pickle.dumps(state))
        except:
            pass

# --- Manejo de cada cliente ---
def handle_client(conn, addr):
    print(f"[+] Jugador {addr} conectado")
    player_id = str(addr)
    with lock:
        players[player_id] = {"x": 0, "y": 0}

    connected = True
    while connected:
        try:
            data = conn.recv(4096)
            if not data:
                break
            # Recibir posición
            pos = pickle.loads(data)
            with lock:
                players[player_id].update(pos)

                # Lógica simple de bandera
                px, py = players[player_id]["x"], players[player_id]["y"]
                if abs(px - flag["x"]) < 30 and abs(py - flag["y"]) < 30:
                    flag["estado"] = player_id  # jugador que tiene la bandera

            broadcast_state()
        except:
            break

    # Cliente desconectado
    print(f"[-] Jugador {addr} desconectado")
    with lock:
        if player_id in players:
            del players[player_id]
        if conn in clients:
            clients.remove(conn)
    conn.close()

# --- Aceptar clientes ---
def start():
    while True:
        conn, addr = server.accept()
        clients.append(conn)
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()

start()
