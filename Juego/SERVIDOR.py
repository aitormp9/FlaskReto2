import socket
import threading
import pickle
import time

# --- CONFIGURACIÓN ---
HOST = '0.0.0.0'
PORT = 2000
MAX_JUGADORES = 4
inicio = time.time()

# Estado global del juego
game_state = {
    "players": {},
    "puntuacion": [0, 0, 0, 0],
    "rondas": [0, 0, 0, 0],
    "bandera": None,
    "estado": "sin empezar",
    "conexiones": [],
    "tiempo": time.time() - inicio  # Lo calcularemos dinámicamente
}

lock = threading.Lock()


def handle_client(conn, addr, player_id):
    global game_state

    # 1. Protocolo estándar: Enviamos ID al conectar
    # Esto es necesario para que tus clientes de juego (pygame) no se rompan
    try:
        conn.send(pickle.dumps(player_id))
    except:
        return

    mi_email_actual = None
    es_flask = False

    try:
        while True:
            # Esperamos datos
            data = conn.recv(8192)
            if not data:
                break

            try:
                datos_recibidos = pickle.loads(data)
            except:
                break

            if datos_recibidos == "API_REQUEST":
                es_flask = True
                with lock:
                    conn.sendall(pickle.dumps(game_state))
                break

            # --- LÓGICA DE JUGADOR NORMAL ---
            with lock:
                # 1. Guardar Email
                if isinstance(datos_recibidos, dict) and "conexion" in datos_recibidos:
                    mi_email_actual = datos_recibidos["conexion"]
                    if mi_email_actual not in game_state["conexiones"]:
                        game_state["conexiones"].append(mi_email_actual)

                # 2. Actualizar Juego
                if isinstance(datos_recibidos, dict):
                    if datos_recibidos.get("banderass"):
                        game_state["bandera"] = datos_recibidos["bandera"]

                    game_state["players"][player_id] = {
                        "x": datos_recibidos.get("x", 0),
                        "y": datos_recibidos.get("y", 0)
                    }

                    idx = player_id - 1
                    game_state["puntuacion"][idx] = datos_recibidos.get("mi_puntuacion", 0)
                    game_state["rondas"][idx] = datos_recibidos.get("mi_ronda", 0)

                    if "bandera" in datos_recibidos:
                        game_state["bandera"] = datos_recibidos["bandera"]

                    # 3. Calcular Estado
                    if 3 in game_state["puntuacion"]:
                        game_state["estado"] = "Terminada"
                    else:
                        game_state["estado"] = "Jugándose"

                # Enviar respuesta al jugador
                conn.sendall(pickle.dumps(game_state))

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        #Borramos jugador
        if not es_flask:
            with lock:
                if player_id in game_state["players"]:
                    del game_state["players"][player_id]
                if mi_email_actual in game_state["conexiones"]:
                    game_state["conexiones"].remove(mi_email_actual)

                if not game_state["players"]:
                    game_state["estado"] = "sin empezar"
                    game_state["bandera"] = None
            print(f"[DESCONEXIÓN] Jugador {player_id} eliminado.")

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

        time.sleep(2)  # Actualiza cada 2 segundos para no saturar la CPU


# --- INICIAR EL MONITOR ---
thread_monitor = threading.Thread(target=monitor_puntuaciones, daemon=True)
thread_monitor.start()


if __name__ == '__main__':
    # Hilo secundario para monitor (opcional)
    threading.Thread(target=monitor_puntuaciones, daemon=True).start()

    print(f"-----------------------\nServidor de Juego en {HOST}:{PORT}\n-----------------------")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    while True:
        conn, addr = server.accept()
        # Asignamos ID (usando lógica simple)
        with lock:
            nuevo_id = next((i for i in range(1, 5) if i not in game_state["players"]), None)

        # Si no hay sitio, cerramos, pero si es Flask, necesitamos dejarle entrar aunque sea id 5
        # Para simplificar, usaremos un ID temporal si está lleno, o reusamos lógica
        if nuevo_id is None:
            nuevo_id = 99  # ID especial temporal

        threading.Thread(target=handle_client, args=(conn, addr, nuevo_id)).start()