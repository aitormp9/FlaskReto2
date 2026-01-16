import requests
from flask import Flask, render_template, request
import threading
app = Flask(__name__, template_folder='templates')
#urlApi = "http://localhost:8080/api/v1"
urlApi = "http://3.233.57.10:8080/api/v1"

estado_bandera =None
estadoActual_Bandera=None
jugador_bandera= None
estado_partida = 'sin empezar'

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

@app.route('/estadoBandera', methods=['GET', 'POST'])
def estadoBandera():
        global estado_bandera, jugador_bandera, estadoActual_Bandera
        print(estado_bandera, estadoActual_Bandera)
        if estado_bandera == None:
            estadoActual_Bandera = "libre"
        else:
            estadoActual_Bandera = "ocupada"
            jugador_bandera = estado_bandera
        return render_template('estadoBandera.html', name="estadoBandera", estado=estado_bandera, jugador=jugador_bandera)
def actualizar_bandera():
    global estado_bandera, jugador_bandera,estadoActual_Bandera
    if estado_bandera==None:
        estadoActual_Bandera = "libre"
    else:
        estadoActual_Bandera = "ocupada"
        jugador_bandera = estado_bandera

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')