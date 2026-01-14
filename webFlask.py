import requests
from flask import Flask, render_template, request
import threading

app = Flask(__name__, template_folder='templates')
urlApi = "http://localhost:8080/api/v1"
#urlApi = "http://3.233.57.10:8080/api/v1/"

estado_bandera = 'libre'
jugador_bandera= None

@app.route('/', methods=['GET', 'POST'])
def inicio():
    return render_template('menuInicio.html', name="menuInicio")

@app.route('/estadoPartida', methods=['GET'])
def estadoPartida():
    return render_template('estadoPartida.html', name="estadoPartida")

@app.route('/jugadoresConectados', methods=['GET'])
def jugadoresConectados():
    response = requests.get(f'{urlApi}/jugadores')
    jugadores = response.json()
    return render_template('jugadoresConectados.html', name="jugadoresConectados", jugadores=jugadores)

@app.route('/posiciones', methods=['GET'])
def posiciones():
    response = requests.get(f"{urlApi}/ranking")
    ranking = response.json()
    return render_template('posiciones.html', name="posiciones", ranking=ranking)

@app.route('/estadoBandera', methods=['GET', 'POST'])
def estadoBandera():
        return render_template('estadoBandera.html', name="estadoBandera")

def actualizar_bandera(nuevo_estado, jugador = None):
    global estado_bandera
    if nuevo_estado in ["libre", "capturada"]:
        estado_bandera = nuevo_estado
        jugador_bandera = jugador

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')