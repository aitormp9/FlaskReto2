import requests

class GameClient:
    #url de la conexión con la API
    def __init__(self):
        self.api_url = "http://3.233.57.10:8080/api/v1"

    #Guardar el resumen de la partida
    def save_game(self, players:dict[int,int],duration:int):
        listajugadores=[]
        for i in range(players[0]):
            jugador={"id":players[0][i],"score":players[1][i]}
            listajugadores.append(jugador)
        data = {
            "jugadores":listajugadores,
            "duracion": duration,
        }
        requests.post(f"{self.api_url}/partidas",json = data)
 
    #Inicia sesión con el email
    def login(self, email:str):
        data = {
            "email":email
        }
        response = requests.post(f"{self.api_url}/jugadores/login", json = data)
        return response.json()
        
# ***** EJEMPLO DE IMPLEMENTACIÓN *****
#def main():
    
    #partida = GameClient()
    # ***** Guardar resumen de partida *****
    #jugadores = {1:20000, 2:3000}
    #duration = 5
    #partida.save_game(jugadores,duration)
    
    # ***** Login de un jugador *****
    #email = "ikyemendez24@lhusurbil.eus"
    #j = partida.login(email)
    #if "error" in j:
     #   print(j["message"])
    #else:
     #   print(j["id"])
    
#main()
