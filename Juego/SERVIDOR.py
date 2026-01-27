import socket
import threading
import pickle
import requests
from flask import Flask, render_template
import time
# --- CONFIGURACIÓN ---
HOST = '0.0.0.0'
PORT = 2000
MAX_JUGADORES = 4
inicio=0
# Estado global del juego: el "puente" entre Sockets y Flask
game_state = {
    "players": {},  # {id: {"x": x, "y": y}}
    "puntuacion": [0, 0, 0, 0],
    "rondas": [0, 0, 0, 0],
    "bandera": None,  # ID o Nombre del poseedor
    "estado": "sin empezar",  # "sin empezar", "jugándose", "terminada"
    "conexiones": [],  # Lista de emails de jugadores activos
    "tiempo":time.time()-inicio,
}

lock = threading.Lock()

# --- FLASK ---
urlApi = "http://3.233.57.10:8080/api/v1"

app = Flask(__name__)  # Flask buscará automáticamente la carpeta 'templates'



@app.route('/')
def inicio():
    return render_template('menuInicio.html', name="menuInicio")


@app.route('/estadoPartida')
def estadoPartida():
    with lock:
        return render_template('estadoPartida.html', name="estadoPartida", estado=game_state["estado"])


@app.route('/jugadoresConectados')
def jugadoresConectados():
    with lock:
        # Mostramos los emails de los jugadores que se han logueado
        return render_template('jugadoresConectados.html', jugadores=game_state["conexiones"])


@app.route('/posiciones')
def posiciones():
    try:
        response = requests.get(f"{urlApi}/ranking", timeout=2)
        ranking = response.json()
    except:
        ranking = []  # Evita que la web caiga si la API externa no responde
    return render_template('posiciones.html', ranking=ranking)


@app.route('/api')
def api():
    with lock:
        return game_state  # Retorna el JSON completo para depuración

estado_actual_bandera=None
@app.route('/estadoBandera')
def estadoBandera():
    global estado_actual_bandera
    if game_state["bandera"] == None:
        estado_actual_bandera = "Libre"
    else:
        estado_actual_bandera = "Ocupado"
        return render_template('estadoBandera.html', estado=estado_actual_bandera, jugador=game_state["bandera"])


# --- SERVIDOR ---

def handle_client(conn, addr, player_id):
    global game_state
    print(f"[NUEVO] Jugador {player_id} conectado.")

    # Variable para recordar el email de este cliente específico
    mi_email_actual = None

    try:
        conn.send(pickle.dumps(player_id))

        while True:
            data = conn.recv(8192)
            if not data:
                break

            datos_recibidos = pickle.loads(data)

            with lock:
                # 1. Guardamos el email para poder borrarlo luego
                if "conexion" in datos_recibidos:
                    mi_email_actual = datos_recibidos["conexion"]
                    # Solo lo añadimos si no está ya en la lista
                    if mi_email_actual not in game_state["conexiones"]:
                        game_state["conexiones"].append(mi_email_actual)

                # 2. Actualizar lógica de juego
                if datos_recibidos.get("banderass"):  # Ojo, tienes un typo aqui "banderass" en tu codigo original
                    game_state["bandera"] = datos_recibidos["bandera"]

                game_state["players"][player_id] = {
                    "x": datos_recibidos["x"],
                    "y": datos_recibidos["y"]
                }

                idx = player_id - 1
                game_state["puntuacion"][idx] = datos_recibidos["mi_puntuacion"]
                game_state["rondas"][idx] = datos_recibidos["mi_ronda"]

                if "bandera" in datos_recibidos:
                    game_state["bandera"] = datos_recibidos["bandera"]

                # 3. Calcular Estado
                if 3 in game_state["puntuacion"]:
                    game_state["estado"] = "Terminada"
                else:
                    # Si hay alguien y no ha terminado, se está jugando
                    game_state["estado"] = "Jugándose"

                # Enviar respuesta global
                conn.sendall(pickle.dumps(game_state))

    except Exception as e:
        print(f"[ERROR] Jugador {player_id}: {e}")

    finally:
        # --- AQUÍ ES DONDE ARREGLAMOS LA DESCONEXIÓN ---
        with lock:
            # 1. Borrar coordenadas
            if player_id in game_state["players"]:
                del game_state["players"][player_id]

            # 2. Borrar de la lista visual de conexiones
            if mi_email_actual in game_state["conexiones"]:
                game_state["conexiones"].remove(mi_email_actual)

            # 3. Actualizar estado si ya no queda nadie
            if not game_state["players"]:  # Si el diccionario está vacío
                game_state["estado"] = "sin empezar"
                # Opcional: Reiniciar bandera y puntuaciones si se van todos
                game_state["bandera"] = None
                # game_state["puntuacion"] = [0, 0, 0, 0]

        conn.close()
        print(f"[DESCONEXIÓN] Jugador {player_id} eliminado.")

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
# --- MAIN ---

def run_flask():
    app.run(debug=False, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    print(f"-----------------------\nIniciando Servidor\n-----------------------")
    threading.Thread(target=run_flask, daemon=True).start()

    print(f"-----------------------\nServidor de Juego en {HOST}:{PORT}\n-----------------------")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    inicio = time.time()
    while True:
        conn, addr = server.accept()
        with lock:
            nuevo_id = next((i for i in range(1, 5) if i not in game_state["players"]), None)
        if nuevo_id:
            threading.Thread(target=handle_client, args=(conn, addr, nuevo_id)).start()
        else:
            conn.close()