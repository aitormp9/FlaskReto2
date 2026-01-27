import socket
import threading
import pickle
import time

# --- CONFIGURACIÓN ---
HOST = '0.0.0.0'
PORT = 2000
MAX_JUGADORES = 4

# Variable para controlar cuándo empieza el cronómetro
inicio_partida = time.time()
tiempo=time.time()-inicio_partida

# Estado global
game_state = {
    "players": {},
    "puntuacion": [0, 0, 0, 0],
    "rondas": [0, 0, 0, 0],
    "bandera": None,
    "estado": "sin empezar",
    "conexiones": [],
    "tiempo": tiempo
}

lock = threading.Lock()


def handle_client(conn, addr, player_id):
    global game_state, inicio_partida

    # 1. Enviar ID al conectar
    try:
        conn.send(pickle.dumps(player_id))
    except:
        return

    mi_email = None
    es_flask = False

    try:
        while True:
            data = conn.recv(8192)
            if not data: break

            try:
                datos = pickle.loads(data)
            except:
                break

            # --- CASO A: ES FLASK PIDIENDO DATOS ---
            if datos == "API_REQUEST":
                es_flask = True
                with lock:
                    # ACTUALIZAMOS EL TIEMPO AQUÍ PARA FLASK
                    game_state["tiempo"] = time.time() - inicio_partida
                    conn.sendall(pickle.dumps(game_state))
                break  # Flask recibe y se va (desconecta)

            # --- CASO B: ES UN JUGADOR ---
            with lock:
                # 1. Gestionar Email
                if isinstance(datos, dict) and "conexion" in datos:
                    mi_email = datos["conexion"]
                    if mi_email and mi_email not in game_state["conexiones"]:
                        game_state["conexiones"].append(mi_email)

                # 2. Actualizar Posiciones y Puntos
                if isinstance(datos, dict):
                    # Actualizar Bandera
                    if "bandera" in datos:
                        game_state["bandera"] = datos["bandera"]

                    # Actualizar Jugador
                    game_state["players"][player_id] = {
                        "x": datos.get("x", 0),
                        "y": datos.get("y", 0)
                    }

                    # Actualizar Puntuación
                    idx = player_id - 1
                    game_state["puntuacion"][idx] = datos.get("mi_puntuacion", 0)
                    game_state["rondas"][idx] = datos.get("mi_ronda", 0)

                    # Verificar Estado
                    if 3 in game_state["puntuacion"]:
                        game_state["estado"] = "Terminada"
                    else:
                        game_state["estado"] = "Jugándose"

                # 3. ACTUALIZAR TIEMPO ANTES DE RESPONDER AL JUGADOR
                game_state["tiempo"] = time.time() - inicio_partida

                # Enviar estado actualizado
                conn.sendall(pickle.dumps(game_state))

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        # Limpieza al desconectar (Solo si NO es Flask)
        if not es_flask:
            with lock:
                if player_id in game_state["players"]:
                    del game_state["players"][player_id]
                if mi_email in game_state["conexiones"]:
                    game_state["conexiones"].remove(mi_email)

                # Si se van todos, reiniciamos el juego y el tiempo
                if not game_state["players"]:
                    print("--- TODOS DESCONECTADOS: REINICIANDO PARTIDA ---")
                    game_state["estado"] = "sin empezar"
                    game_state["bandera"] = None
                    inicio_partida = time.time()  # REINICIAR CRONÓMETRO

        conn.close()
def monitor_puntuaciones():
    while True:
        print("\n--- ESTADO DE LA PARTIDA ---")
        with lock:
            for i in range(MAX_JUGADORES):
                p_id = i + 1
                conectado = "CONECTADO" if p_id in game_state["players"] else "---"
                puntos = game_state["puntuacion"][i]
                rondas = game_state["rondas"][i]
                print(f"Jugador {p_id} ({conectado}): {puntos} Pts | {rondas} Rondas")
            print("Bandera", game_state["bandera"])
            print("Conexion", game_state["conexiones"])
        print("----------------------------")

        time.sleep(5)

# --- INICIAR EL MONITOR ---
thread_monitor = threading.Thread(target=monitor_puntuaciones, daemon=True)
thread_monitor.start()




# --- ARRANQUE ---
if __name__ == '__main__':
    print(f"--- SERVER CORRIENDO EN {HOST}:{PORT} ---")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    while True:
        conn, addr = server.accept()

        with lock:
            nuevo_id = next((i for i in range(1, 5) if i not in game_state["players"]), None)

        if nuevo_id is None:
            nuevo_id = 99

        threading.Thread(target=handle_client, args=(conn, addr, nuevo_id)).start()