import pygame
import time
import socket
import pickle
from jugador import jugador
from casa import casa
from muro import muro
from bandera import bandera
from gamerequests.jugador import GameClient
import webFlask

def send_position(x, y):
    try:
        client.sendall(pickle.dumps({"x": x, "y": y}))
        return pickle.loads(client.recv(4096))
    except:
        return None

def login():
    global login,idBBDD,partida
    email=input("Ingresa tu email: ")
    j = partida.login(email)
    if "error" in j:
       print(j["message"])
    else:
        print(j["id"])
        idBBDD=j["id"]
        login=True

def finPartida():
    global puntuacion,DuracionPartida,partida,idBBDD
    for i in range(len(puntuacion)):
        if rondas[i]==3:
            print(puntuacion[i])
            print(f"El Jugador {i+1} ha ganado la partida")
            tiempo=(time.time()-DuracionPartida)
            horas = tiempo // 3600
            minutos = (tiempo % 3600) // 60
            segundos = tiempo % 60
            partida.save_game({idBBDD: puntuacion[mi_id-1]},tiempo)
            pygame.quit()
            client.close()
            exit()

def dibujar():
    muro11.draw()
    muro12.draw()
    muro13.draw()
    muro14.draw()
    muro21.draw()
    muro22.draw()
    muro23.draw()
    muro24.draw()
    muro31.draw()
    muro32.draw()
    muro33.draw()
    muro34.draw()
    muro41.draw()
    muro42.draw()
    muro43.draw()
    muro44.draw()
    casa1.draw()
    casa2.draw()
    casa3.draw()
    casa4.draw()
    p1.draw()
    p2.draw()
    p3.draw()
    p4.draw()
    bandera.draw()

def colisiones(player):
    #ColisionConlas esquinas de screen
    if player.x < 0:
        player.x = 0
    if player.x + player.anchura > 1280:
        player.x = 1280 - player.anchura

    # Límites verticales
    if player.y < 0:
        player.y = 0
    if player.y + player.altura > 720:
        player.y = 720 - player.altura
        # Colision con muros
    for muro in muros:
        if (player.getrect().colliderect(muro.getrect())):
            player.x, player.y = player.old_x, player.old_y
def estadobandera():
    global puntuacion
    for jugador in jugadores:
        # Robo de la bandera
        if bandera.jugador and bandera.jugador != jugador:
            if jugador.getrect().colliderect(bandera.getrect()):
                print(bandera.jugador)
                for pillado in jugadores:
                    if pillado is bandera.jugador:
                        pillado.x = pillado.xinicio
                        pillado.y = pillado.yinicio
                        bandera.jugador = None

        # Tomar la bandera del suelo
        if bandera.jugador==None and jugador.getrect().colliderect(bandera.getrect()):
            bandera.jugador = jugador
            puntuacion[mi_id-1]+=1
            webFlask.jugador_bandera=jugador
            print(jugador)

        # Transportar la bandera con el jugador
        if bandera.jugador == jugador:
            bandera.x = jugador.x + 20
            bandera.y = jugador.y

        if bandera.jugador==p1 and casa1.getrect().colliderect(jugador.getrect()):
                bandera.x = casa1.x + 7
                bandera.y = casa1.y + 7
                bandera.jugador = casa1
                bandera.tiempo=time.time()
        if bandera.jugador==p2 and casa2.getrect().colliderect(jugador.getrect()):
                bandera.x = casa2.x + 7
                bandera.y = casa2.y + 7
                bandera.jugador = casa2
                bandera.tiempo=time.time()
        if bandera.jugador == p3 and casa3.getrect().colliderect(jugador.getrect()):
            bandera.x = casa3.x + 7
            bandera.y = casa3.y + 7
            bandera.jugador = casa3
            bandera.tiempo = time.time()
        if bandera.jugador == p4 and casa4.getrect().colliderect(jugador.getrect()):
            bandera.x = casa4.x + 7
            bandera.y = casa4.y + 7
            bandera.jugador = casa4
            bandera.tiempo = time.time()

        if bandera.jugador in (casa1, casa2, casa3, casa4):
            if bandera.jugador==jugador.casa:
                if bandera.esperando is False:
                    bandera.tiempo = time.time()
                    bandera.esperando=True
                    print(puntuacion)
                if time.time() - bandera.tiempo >= 2:
                    puntuacion[mi_id-1]+=4
                    rondas[mi_id-1]+=1
                    reiniciar()
                    bandera.esperando=False


def reiniciar():
    p1.x=25
    p1.y=25
    p2.x=1245
    p2.y=25
    p3.x=25
    p3.y=685
    p4.x=1245
    p4.y=685
    bandera.x=640
    bandera.y=360
    bandera.jugador=None
# --- CONFIGURACIÓN RED ---
HOST = '192.168.25.46'
PORT = 2000
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
mi_id = pickle.loads(client.recv(4096))
print(f"Soy el jugador número: {mi_id}")
idBBDD=0
partida = GameClient()
DuracionPartida = time.time()
# --- INICIO PYGAME (Igual que el tuyo) ---
pygame.init()
login()
while login==True:
    screen = pygame.display.set_mode((1280, 720))
    # ... (Aquí van tus cargas de imágenes, casas, muros y jugadores tal cual los tienes)
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    imagen=pygame.image.load('imagen/fondo.jpg').convert_alpha()
    fondo=pygame.transform.scale(imagen,(1280,720))
    clock = pygame.time.Clock()
    casa1=casa(screen,0,0)
    p1=jugador(screen,25,25,casa1,'imagen/p1.png')
    casa2=casa(screen,1210,0)
    p2=jugador(screen,1245,25,casa2,'imagen/p2.png')
    casa3=casa(screen,0,650)
    p3=jugador(screen,25,685,casa3,'imagen/p3.png')
    casa4=casa(screen,1210,650)
    p4=jugador(screen,1245,685,casa4,'imagen/p4.png')
    inicio = time.time();
    # --- ZONA 1 (Arriba-Izquierda) | Rango X: 100-540, Y: 100-260 ---
    muro11 = muro(screen, 150, 100, 150, 30)  # Barra horizontal superior
    muro12 = muro(screen, 400, 100, 30, 120)  # Barra vertical derecha
    muro13 = muro(screen, 150, 200, 100, 30)  # Barra horizontal inferior
    muro14 = muro(screen, 300, 160, 40, 40)  # Bloque central

    # --- ZONA 2 (Arriba-Derecha) | Rango X: 740-1180, Y: 100-260 ---
    muro21 = muro(screen, 940, 100, 150, 30)
    muro22 = muro(screen, 800, 100, 30, 120)
    muro23 = muro(screen, 940, 200, 100, 30)
    muro24 = muro(screen, 880, 160, 40, 40)

    # --- ZONA 3 (Abajo-Izquierda) | Rango X: 100-540, Y: 460-620 ---
    muro31 = muro(screen, 150, 590, 150, 30)
    muro32 = muro(screen, 400, 460, 30, 120)
    muro33 = muro(screen, 150, 460, 100, 30)
    muro34 = muro(screen, 300, 520, 40, 40)

    # --- ZONA 4 (Abajo-Derecha) | Rango X: 740-1180, Y: 460-620 ---
    muro41 = muro(screen, 940, 590, 150, 30)
    muro42 = muro(screen, 800, 460, 30, 120)
    muro43 = muro(screen, 940, 460, 100, 30)
    muro44 = muro(screen, 880, 520, 40, 40)
    bandera=bandera(screen)
    muros=[]
    casas=[]
    jugadores=[]
    jugadores.append(p1)
    jugadores.append(p2)
    jugadores.append(p3)
    jugadores.append(p4)
    muros.append(muro11)
    muros.append(muro12)
    muros.append(muro13)
    muros.append(muro14)
    muros.append(muro21)
    muros.append(muro22)
    muros.append(muro23)
    muros.append(muro24)
    muros.append(muro31)
    muros.append(muro32)
    muros.append(muro33)
    muros.append(muro34)
    muros.append(muro41)
    muros.append(muro42)
    muros.append(muro43)
    muros.append(muro44)
    casas.append(casa1)
    casas.append(casa2)
    casas.append(casa3)
    casas.append(casa4)
    velocidad=2;
    pillado=False
    p_local = jugadores[mi_id-1]
    puntuacion=[0,0,0,0]
    login=False
    rondas = [0,0,0,0]

    # BUCLE PRINCIPAL
    while True:
            screen.blit(fondo, (0, 0))
            # 1. Movimiento del local (p1)
            keys = pygame.key.get_pressed()
            p_local.old_x, p_local.old_y = p_local.x, p_local.y  # Guardar para colisiones
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: p_local.x -= velocidad
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: p_local.x += velocidad
            if keys[pygame.K_UP] or keys[pygame.K_w]: p_local.y -= velocidad
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: p_local.y += velocidad

            colisiones(p_local)  # Comprobar colisión local antes de enviar

            # --- En main.py ---
            state = send_position(p_local.x, p_local.y)

            if state and 'players' in state:
                # Recorremos el diccionario usando la CLAVE (que es el ID real)
                for p_id, pdata in state['players'].items():
                    if p_id != mi_id:
                        # IMPORTANTE: Usamos p_id directamente para saber qué muñeco mover
                        # Si p_id es 1, movemos jugadores[0]. Si es 3, movemos jugadores[2]
                        indice = p_id - 1
                        if 0 <= indice < len(jugadores):
                            jugadores[indice].x = pdata['x']
                            jugadores[indice].y = pdata['y']
            # 3. Lógica y Dibujo
            estadobandera()
            dibujar()
            finPartida()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    client.close()
                    exit()

            pygame.display.update()
            clock.tick(60)