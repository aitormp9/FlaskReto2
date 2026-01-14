import socket
import threading
import pickle

HOST = '0.0.0.0'
PORT = 2000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print("Servidor iniciado, esperando jugadores...")

players = {}
flag = {"x": 640, "y": 360, "jugador": None}
clients = []
lock = threading.Lock()

def broadcast_state():
    state = {"players": players, "flag": flag}
    for c in clients:
        try:
            c.sendall(pickle.dumps(state))
        except:
            pass

def handle_client(conn, addr):
    player_id = str(addr)
    with lock:
        players[player_id] = {"x": 0, "y": 0, "x_inicio": 0, "y_inicio": 0}
    clients.append(conn)
    print(f"[+] Jugador {player_id} conectado")

    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            pos = pickle.loads(data)

            with lock:
                players[player_id]["x"] = pos.get("x", players[player_id]["x"])
                players[player_id]["y"] = pos.get("y", players[player_id]["y"])

                # Lógica bandera
                px, py = players[player_id]["x"], players[player_id]["y"]
                fx, fy = flag["x"], flag["y"]

                # Tomar bandera si está libre
                if flag["jugador"] is None and abs(px - fx) < 30 and abs(py - fy) < 30:
                    flag["jugador"] = player_id

                # Robo de bandera
                if flag["jugador"] is not None and flag["jugador"] != player_id:
                    jugador_con_bandera = flag["jugador"]
                    bx, by = players[jugador_con_bandera]["x"], players[jugador_con_bandera]["y"]
                    if abs(px - bx) < 30 and abs(py - by) < 30:
                        # Devuelve la bandera
                        players[jugador_con_bandera]["x"] = players[jugador_con_bandera]["x_inicio"]
                        players[jugador_con_bandera]["y"] = players[jugador_con_bandera]["y_inicio"]
                        flag["jugador"] = None

            broadcast_state()

        except:
            break

    print(f"[-] Jugador {player_id} desconectado")
    with lock:
        if player_id in players:
            del players[player_id]
        if conn in clients:
            clients.remove(conn)
    conn.close()

def start():
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

start()
