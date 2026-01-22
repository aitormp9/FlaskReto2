import requests
from flask import Flask, render_template, request
import threading
import sys
import os

# 1. Configuración de rutas
base_path = os.path.dirname(os.path.abspath(__file__))
juego_path = os.path.join(base_path, 'Juego')

if juego_path not in sys.path:
    sys.path.append(juego_path)

# 2. Variables de estado globales
# IMPORTANTE: Estas variables las actualizará mainJuego.py directamente
jugador_con_bandera = None
estado_actual_bandera = "libre"
estado_partida = 'sin empezar'
urlApi = "http://3.233.57.10:8080/api/v1"
app = Flask(__name__, template_folder='templates')
@app.route('/', methods=['GET', 'POST'])
def inicio():
    return render_template('menuInicio.html', name="menuInicio")

@app.route('/estadoPartida', methods=['GET'])
def estadoPartida():
    return render_template('estadoPartida.html', name="estadoPartida", estado=estado_partida)
def  actualizarPartida(nuevo_estadoPartida):
    global estado_partida
    if nuevo_estadoPartida in ["sin empezar","jugándose","terminada"]:
        estado_partida = nuevo_estadoPartida

@app.route('/jugadoresConectados', methods=['GET'])
def jugadoresConectados(nuevoJugador):
    response = requests.get(f'{urlApi}/jugadores')
    jugadores = response.json()
    return render_template('jugadoresConectados.html', name="jugadoresConectados", jugadores=jugadores)

@app.route('/posiciones', methods=['GET'])
def posiciones():
    response = requests.get(f"{urlApi}/ranking")
    ranking = response.json()
    return render_template('posiciones.html', name="posiciones", ranking=ranking)

@app.route('/estadoBandera')
def estadoBandera():
    # Aquí Flask solo lee las variables que el juego le "empuja"
    return render_template('estadoBandera.html',
                           estado=estado_actual_bandera,
                           jugador=jugador_con_bandera)
def actualizar_bandera():
    global estado_bandera, jugador_bandera,estadoActual_Bandera
    if estado_bandera==None:
        estadoActual_Bandera = "libre"
    else:
        estadoActual_Bandera = "ocupada"
        jugador_bandera = estado_bandera

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')