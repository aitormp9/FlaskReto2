import socket
import threading
import pickle
import requests
from flask import Flask, render_template  # Corregido: render_template es la función correcta
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

state_lock = threading.Lock()
urlApi = "http://3.233.57.10:8080/api/v1"

app = Flask(__name__)  # Flask buscará automáticamente la carpeta 'templates'


# --- RUTAS DE FLASK ---

@app.route('/')
def inicio():
    return render_template('menuInicio.html', name="menuInicio")


@app.route('/estadoPartida')
def estadoPartida():
    with state_lock:
        return render_template('estadoPartida.html', name="estadoPartida", estado=game_state["estado"])


@app.route('/jugadoresConectados')
def jugadoresConectados():
    with state_lock:
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
    with state_lock:
        return game_state  # Retorna el JSON completo para depuración

estadoActual_Bandera=None
estado_bandera=None
jugador_bandera=game_state["bandera"]
estado_actual_bandera=None
@app.route('/estadoBandera')
def estadoBandera():
    global estado_actual_bandera
    if game_state["bandera"] == None:
        estado_actual_bandera = "Libre"
    else:
        estado_actual_bandera = "Ocupado"
        return render_template('estadoBandera.html', estado=estado_actual_bandera, jugador=game_state["bandera"])


# --- LÓGICA DE SOCKETS ---

def handle_client(conn, addr, player_id):
    global game_state
    print(f"[NUEVO] Jugador {player_id} conectado.")

    try:
        conn.send(pickle.dumps(player_id))

        while True:
            data = conn.recv(8192)
            if not data:
                break

            datos_recibidos = pickle.loads(data)

            with state_lock:
                game_state["estado"] = "jugándose"
                if datos_recibidos.get("banderass"):
                    game_state["bandera"] = datos_recibidos["bandera"]
                # Actualizar posición
                game_state["players"][player_id] = {
                    "x": datos_recibidos["x"],
                    "y": datos_recibidos["y"]
                }

                # Actualizar puntos y rondas
                idx = player_id - 1
                game_state["puntuacion"][idx] = datos_recibidos["mi_puntuacion"]
                game_state["rondas"][idx] = datos_recibidos["mi_ronda"]

                # Actualizar bandera y conexión (si el cliente los envía)
                if "bandera" in datos_recibidos:
                    game_state["bandera"] = datos_recibidos["bandera"]

                if "conexion" in datos_recibidos and datos_recibidos["conexion"] not in game_state["conexiones"]:
                    game_state["conexiones"].append(datos_recibidos["conexion"])

                # Enviar respuesta global
                conn.sendall(pickle.dumps(game_state))

    except Exception as e:
        print(f"[ERROR] Jugador {player_id}: {e}")
    finally:
        with state_lock:
            if player_id in game_state["players"]:
                del game_state["players"][player_id]
        conn.close()


# --- LANZAMIENTO ---

def run_flask():
    # use_reloader=False es vital cuando usas hilos para evitar que Flask se reinicie solo
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)


if __name__ == '__main__':
    print(f"Iniciando Servidor Web en puerto 5000...")
    threading.Thread(target=run_flask, daemon=True).start()

    print(f"Servidor de Juego en {HOST}:{PORT}. Esperando jugadores...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    inicio = time.time()
    while True:
        conn, addr = server.accept()
        with state_lock:
            nuevo_id = next((i for i in range(1, 5) if i not in game_state["players"]), None)

        if nuevo_id:
            threading.Thread(target=handle_client, args=(conn, addr, nuevo_id)).start()
        else:
            conn.close()