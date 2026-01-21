import pygame
import time
import socket
import pickle
import threading
from jugador import jugador
from casa import casa
from muro import muro
from bandera import bandera
from gamerequests.jugador import GameClient
# --- CONFIGURACIÓN RED ---
HOST = 'localhost'
PORT = 2000
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
mi_id = pickle.loads(client.recv(4096))
color=None
if mi_id==1:
    color="rojo"
if mi_id==2:
    color="Azul"
if mi_id==3:
    color="verde"
if mi_id==4:
    color="Naranja"
print(f"Jugador Número: {mi_id} = Color: {color}")
idBBDD=0
DuracionPartida = time.time()
lock=threading.Lock()
partida = GameClient()
sesion=False


def envioPosicion(x, y):
    global puntuacion, rondas  # Importante para actualizar las variables globales
    try:
        paquete = {
            "x": x,
            "y": y,
            "mi_puntuacion": puntuacion[mi_id - 1],  # Solo envío MIS puntos actuales
            "mi_ronda": rondas[mi_id - 1]
        }
        client.sendall(pickle.dumps(paquete))

        respuesta = client.recv(8192)
        estado_global = pickle.loads(respuesta)

        # Sincronizamos las listas locales con lo que dice el servidor
        puntuacion = estado_global["puntuacion"]
        rondas = estado_global["rondas"]

        return estado_global
    except:
        return None
def iniciosesion():#Funcion de iniciar sesion vinculado a Odoo
    global sesion,idBBDD,partida
    email=input("Ingresa tu email: ")
    j = partida.login(email)
    if "error" in j:
       print(j["message"])
    else:
        print(+j["id"]) #id del jugador en la bbdd
        idBBDD=j["id"]
        sesion=True
        print(sesion)

def contador():#Funcion para contador
    posiciones = [
        (60, 20),  # Jugador 1 (Arriba Izquierda)
        (1220, 20),  # Jugador 2 (Arriba Derecha)
        (60, 680),  # Jugador 3 (Abajo Izquierda)
        (1220, 680)  # Jugador 4 (Abajo Derecha)
    ]

    for i in range(len(rondas)):
        texto = f"{rondas[i]}"
        texto_surface = fuente_contador.render(texto, True, (255,255,255))

        rect = texto_surface.get_rect()
        if posiciones[i][0] > 640:
            rect.topright = posiciones[i]
        else:
            rect.topleft = posiciones[i]

        screen.blit(texto_surface, rect)

def finPartida():#Verificacion de final de partida y envio de datos
    global puntuacion,DuracionPartida,partida,idBBDD
    for i in range(len(puntuacion)):
        if rondas[i]==3:
            with lock:
                screen.blit(fondo,(0,0))
                dibujar()
                contador()
            pygame.display.update()
            time.sleep(1)
            print(rondas[i])
            print(f"El Jugador {i+1} ha ganado la partida")
            tiempo = int(time.time() - DuracionPartida)

            horas = tiempo // 3600
            minutos = (tiempo % 3600) // 60
            segundos = tiempo % 60

            duracion = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
            print(duracion)
            partida.save_game({idBBDD: puntuacion[mi_id-1]},duracion)
            pygame.quit()
            client.close()
            exit()

def dibujar():#Funcion para dibujar todos los objetos
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
    bandera.draw()#

def colisiones(player):#Todas las colisiones excepto la bandera
    if player.x < 0:
        player.x = 0
    if player.x + player.anchura > 1280:
        player.x = 1280 - player.anchura

    if player.y < 0:
        player.y = 0
    if player.y + player.altura > 720:
        player.y = 720 - player.altura

    for muro in muros:
        if (player.getrect().colliderect(muro.getrect())):
            player.x, player.y = player.old_x, player.old_y


def estadobandera():
    global puntuacion, rondas
    for jugador in jugadores:
        # 1. ROBO DE LA BANDERA
        # Si alguien lleva la bandera y otro lo toca, el que la llevaba vuelve al inicio
        if bandera.jugador and bandera.jugador != jugador:
            if jugador.getrect().colliderect(bandera.getrect()):
                for pillado in jugadores:
                    if pillado is bandera.jugador:
                        pillado.x = pillado.xinicio
                        pillado.y = pillado.yinicio
                        bandera.x = 640
                        bandera.y = 360
                        bandera.jugador = None

        # 2. TOMAR LA BANDERA DEL SUELO
        if bandera.jugador == None and jugador.getrect().colliderect(bandera.getrect()):
            bandera.jugador = jugador
            # Solo sumamos el punto de "recogida" si el que la toca eres TÚ
            if jugador == p_local:
                puntuacion[mi_id - 1] += 1
            print(f"Bandera recogida por: {jugador}")

        # 3. TRANSPORTAR LA BANDERA
        if bandera.jugador == jugador:
            bandera.x = jugador.x + 20
            bandera.y = jugador.y

        # 4. COLISIÓN CON LAS 4 CASAS
        # Casa 1
        if bandera.jugador == p1 and casa1.getrect().colliderect(jugador.getrect()):
            bandera.x, bandera.y = casa1.x + 30, casa1.y + 10
            bandera.jugador = casa1
            bandera.tiempo = time.time()
        # Casa 2
        elif bandera.jugador == p2 and casa2.getrect().colliderect(jugador.getrect()):
            bandera.x, bandera.y = casa2.x + 30, casa2.y + 10
            bandera.jugador = casa2
            bandera.tiempo = time.time()
        # Casa 3
        elif bandera.jugador == p3 and casa3.getrect().colliderect(jugador.getrect()):
            bandera.x, bandera.y = casa3.x + 30, casa3.y + 10
            bandera.jugador = casa3
            bandera.tiempo = time.time()
        # Casa 4
        elif bandera.jugador == p4 and casa4.getrect().colliderect(jugador.getrect()):
            bandera.x, bandera.y = casa4.x + 30, casa4.y + 10
            bandera.jugador = casa4
            bandera.tiempo = time.time()

        # 5. LÓGICA DE PUNTUACIÓN Y RONDAS
        # Si la bandera está en una casa y es la casa de ese jugador
        if bandera.jugador in (casa1, casa2, casa3, casa4):
            if bandera.jugador == jugador.casa:
                if bandera.esperando is False:
                    bandera.tiempo = time.time()
                    bandera.esperando = True

                # Si pasa 1 segundo la bandera en la casa
                if time.time() - bandera.tiempo >= 1:
                    # MUY IMPORTANTE: Solo sumas si el jugador que ha anotado eres TÚ
                    if jugador == p_local:
                        puntuacion[mi_id - 1] += 4
                        rondas[mi_id - 1] += 1
                        reiniciar()  # Resetea posiciones
                        contador()  # Actualiza visualmente
                    bandera.esperando = False
def reiniciar():
    p1.x=25
    p1.y=35
    p2.x=1232
    p2.y=35
    p3.x=25
    p3.y=685
    p4.x=1230
    p4.y=685
    bandera.x=640
    bandera.y=360
    bandera.jugador=None

pygame.init()
pygame.display.set_caption("Captura la bandera - Game Hub")
iniciosesion()
if sesion:
    pygame.init()
    fuente_contador = pygame.font.Font(None, 32)
    screen = pygame.display.set_mode((1280, 720))
    imagen=pygame.image.load('imagen/fondo.jpg').convert_alpha()
    fondo=pygame.transform.scale(imagen,(1280,720))
    clock = pygame.time.Clock()
    #Creacion de casas y jugadores
    casa1=casa(screen,0,0)
    p1=jugador(screen,25,35,casa1,'imagen/p1.png')
    casa2=casa(screen,1210,0)
    p2=jugador(screen,1232,35,casa2,'imagen/p2.png')
    casa3=casa(screen,0,650)
    p3=jugador(screen,25,685,casa3,'imagen/p3.png')
    casa4=casa(screen,1210,650)
    p4=jugador(screen,1230,685,casa4,'imagen/p4.png')
    inicio = time.time();
    #ZONA 1 (Arriba-Izquierda) | Rango X: 100-540, Y: 100-260
    muro11 = muro(screen, 150, 100, 150, 30)  # Barra horizontal superior
    muro12 = muro(screen, 400, 100, 30, 120)  # Barra vertical derecha
    muro13 = muro(screen, 150, 200, 100, 30)  # Barra horizontal inferior
    muro14 = muro(screen, 300, 160, 40, 40)  # Bloque central

    #ZONA 2 (Arriba-Derecha) | Rango X: 740-1180, Y: 100-260
    muro21 = muro(screen, 940, 100, 150, 30)
    muro22 = muro(screen, 800, 100, 30, 120)
    muro23 = muro(screen, 940, 200, 100, 30)
    muro24 = muro(screen, 880, 160, 40, 40)

    #ZONA 3 (Abajo-Izquierda) | Rango X: 100-540, Y: 460-620
    muro31 = muro(screen, 150, 590, 150, 30)
    muro32 = muro(screen, 400, 460, 30, 120)
    muro33 = muro(screen, 150, 460, 100, 30)
    muro34 = muro(screen, 300, 520, 40, 40)

    #ZONA 4 (Abajo-Derecha) | Rango X: 740-1180, Y: 460-620
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
    rondas = [0,0,0,0]

    # BUCLE PRINCIPAL
    while True:
            screen.blit(fondo, (0, 0))
            with lock:
                dibujar()
                contador()
                estadobandera()
            # 1. Movimiento del jugador
            keys = pygame.key.get_pressed()
            p_local.old_x, p_local.old_y = p_local.x, p_local.y  # Guardar para colisiones
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: p_local.x -= velocidad
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: p_local.x += velocidad
            if keys[pygame.K_UP] or keys[pygame.K_w]: p_local.y -= velocidad
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: p_local.y += velocidad
            try:
                colisiones(p_local)  # Comprobar colisiones antes de enviar
            except:
                print("Error con las colisiones")
            try:
                state = envioPosicion(p_local.x, p_local.y)
            except:
                print("Error con el envio de datos")
            # --- Dentro del bucle principal del cliente ---
            state = envioPosicion(p_local.x, p_local.y)

            if state:
                # 1. Actualizar posiciones de los demás
                for p_id, pdata in state['players'].items():
                    if p_id != mi_id:
                        indice = p_id - 1
                        if 0 <= indice < len(jugadores):
                            jugadores[indice].x = pdata['x']
                            jugadores[indice].y = pdata['y']

                # 2. Sincronizar puntos de los OTROS, pero mantener los MÍOS
                for i in range(len(puntuacion)):
                    if i != (mi_id - 1):  # Si no soy yo, actualizo con lo que dice el servidor
                        puntuacion[i] = state['puntuacion'][i]
                        rondas[i] = state['rondas'][i]
                    else:
                        # Si soy yo, el servidor se actualiza con mis datos locales
                        # (No hacemos nada porque nuestra variable local ya es la correcta)
                        pass
            try:
                finPartida()
            except Exception as e:
                print(f"Error detectado: {e}")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    client.close()
                    exit()

            pygame.display.update()
            clock.tick(60)