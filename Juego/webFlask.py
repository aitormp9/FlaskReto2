from flask import Flask, render_template
import socket
import pickle
import requests

app = Flask(__name__)

# Configuración de dónde está el servidor de juego (mismo PC = localhost)
GAME_SERVER_IP = '127.0.0.1'
GAME_SERVER_PORT = 2000
urlApi = "http://3.233.57.10:8080/api/v1"


def obtener_estado_del_server():
    """Esta función es el 'espía' que va al server y trae los datos"""
    try:
        # 1. Conectamos al servidor de juego
        cliente_flask = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente_flask.connect((GAME_SERVER_IP, GAME_SERVER_PORT))

        # 2. El servidor nos manda un ID nada más conectar (protocolo actual)
        # Lo recibimos pero lo ignoramos porque somos Flask, no un jugador
        _ = cliente_flask.recv(4096)

        # 3. Enviamos la clave secreta para pedir datos
        cliente_flask.send(pickle.dumps("API_REQUEST"))

        # 4. Recibimos el estado completo del juego
        data = cliente_flask.recv(8192)
        estado = pickle.loads(data)

        cliente_flask.close()
        return estado
    except Exception as e:
        print(f"Error conectando al juego: {e}")
        # Retornamos un estado vacío de seguridad para que la web no se caiga
        return {
            "estado": "OFFLINE",
            "players": {},
            "puntuacion": [0, 0, 0, 0],
            "rondas": [0, 0, 0, 0],
            "conexiones": [],
            "bandera": None,
            "tiempo": 0
        }


@app.route('/')
def inicio():
    return render_template('menuInicio.html', name="menuInicio")


@app.route('/estadoPartida')
def estadoPartida():
    data = obtener_estado_del_server()
    return render_template('estadoPartida.html', name="estadoPartida", estado=data["estado"])


@app.route('/jugadoresConectados')
def jugadoresConectados():
    data = obtener_estado_del_server()
    return render_template('jugadoresConectados.html', jugadores=data["conexiones"])


@app.route('/posiciones')
def posiciones():
    try:
        response = requests.get(f"{urlApi}/ranking", timeout=2)
        ranking = response.json()
    except:
        ranking = []
    return render_template('posiciones.html', ranking=ranking)


@app.route('/api')
def api():
    return obtener_estado_del_server()


@app.route('/estadoBandera')
def estadoBandera():
    data = obtener_estado_del_server()
    if data["bandera"] is None:
        estado = "Libre"
    else:
        estado = "Ocupado"
    return render_template('estadoBandera.html', estado=estado, jugador=data["bandera"])


if __name__ == '__main__':
    print("Iniciando Servidor WEB en puerto 5000...")
    app.run(debug=True, host='0.0.0.0', port=5000)