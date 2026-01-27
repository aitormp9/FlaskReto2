import pygame
import time
import socket
import pickle
import threading
from Figuras.jugador import jugador
from Figuras.casa import casa
from Figuras.muro import muro
from Figuras.bandera import bandera
from gamerequests.jugador import GameClient

# --- CONFIGURACIÓN RED ---
HOST = '192.168.25.46'
PORT = 2000
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
mi_id = pickle.loads(client.recv(4096))
color={1:"Rojo",2:"Azul",3:"Verde",4:"Naranja"}

print(f"Color del Jugador: {color[mi_id]}")
idBBDD=0
DuracionPartida = time.time()
lock=threading.Lock()
partida = GameClient()
sesion=False
tiempo=0
puntuacion=[0,0,0,0]
rondas=[0,0,0,0]
conexion=None

def envioPosicion(x, y):#La informacion que gestionamos con los sockets
    global puntuacion, rondas,tiempo,bandera  # Importante para actualizar las variables globales
    try:
        paquete = {
            "x": x,
            "y": y,
            "mi_puntuacion": puntuacion[mi_id - 1],  # Solo envío MIS puntos actuales
            "mi_ronda": rondas[mi_id - 1],
            "bandera":bandera.jugador,
            "conexion":conexion
        }
        #print(bandera.jugador)
        client.sendall(pickle.dumps(paquete))

        respuesta = client.recv(8192)
        estado_global = pickle.loads(respuesta)

        # Sincronizamos las listas locales con lo que dice el servidor
        puntuacion = estado_global["puntuacion"]
        rondas = estado_global["rondas"]
        tiempo=estado_global["tiempo"]
        return estado_global
    except:
        return None

def iniciosesion():#Funcion de iniciar sesion vinculado a Odoo
    global sesion,idBBDD,partida,conexion
    email=input("Ingresa tu email: ")
    j = partida.login(email)
    if "error" in j:
       print(j["message"])
    else:
        #print(+j["id"]) #id del jugador en la bbdd
        conexion=email
        idBBDD=j["id"]
        sesion=True
        #print(sesion)

def contador():#Contador y marcadores que se muestran en pantalla
    global tiempo
    tiempo_segundos = int(tiempo)
    horas = tiempo_segundos // 3600
    minutos = (tiempo_segundos % 3600) // 60
    segundos = tiempo_segundos % 60
    texto_tiempo = f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    posiciones = [
        (60, 20),    # P1
        (1220, 20),  # P2
        (60, 680),   # P3
        (1220, 680), # P4
        (640, 680)   # CRONÓMETRO
    ]

    # 2. Dibujar el Cronómetro (Usa el índice 4)
    surf_tiempo = fuente_contador.render(texto_tiempo, True, (255, 255, 255))
    rect_tiempo = surf_tiempo.get_rect(midbottom=posiciones[4])
    screen.blit(surf_tiempo, rect_tiempo)

    # 3. Dibujar las rondas de los jugadores
    for i in range(len(rondas)):
        texto_ronda = f"{rondas[i]}"
        surf_ronda = fuente_contador.render(texto_ronda, True, (255, 255, 255))
        rect_ronda = surf_ronda.get_rect()

        # Alineación dinámica (Derecha o Izquierda)
        if posiciones[i][0] > 640:
            rect_ronda.topright = posiciones[i]
        else:
            rect_ronda.topleft = posiciones[i]

        screen.blit(surf_ronda, rect_ronda)


def finPartida():#Gestion final de la partida
    global rondas, puntuacion, tiempo, partida, idBBDD
    for i in range(len(rondas)):
        if rondas[i] >= 3:
            envioPosicion(p_local.x, p_local.y)
            screen.blit(fondo, (0, 0))
            dibujar()
            contador()
            pygame.display.update()
            vencedor_id = i + 1
            nombre_color = color[vencedor_id]
            print(f"¡El Jugador {nombre_color} ha ganado!")
            if vencedor_id == mi_id:
                tiempos = int(time.time() - tiempo)
                duracion = f"{tiempos // 3600:02d}:{(tiempos % 3600) // 60:02d}:{tiempos % 60:02d}"
                partida.save_game({idBBDD: puntuacion[mi_id - 1]}, duracion)
            time.sleep(2)
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
    bandera.draw()

def colisiones(player):#Control de todas las colisiones excepto la bandera
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


def estadobandera():#Todo lo relacionado con la bandera se gestiona aqui
    global rondas, puntuacion

    for jugador in jugadores:
        # 1. ROBO DE LA BANDERA
        # ERROR ESTABA AQUI: bandera.jugador != jugador
        # CORRECCION: bandera.jugador != jugador.nombre
        if bandera.jugador and bandera.jugador != jugador.nombre and bandera.jugador not in casas:

            # Verificamos colisión
            if jugador.getrect().colliderect(bandera.getrect()):
                # Si alguien toca al portador, el portador vuelve al inicio
                for pillado in jugadores:
                    # Aquí también debemos comparar nombres para encontrar al portador
                    if pillado.nombre == bandera.jugador:
                        pillado.x, pillado.y = pillado.xinicio, pillado.yinicio

                # Resetear bandera
                bandera.x, bandera.y = 640, 360
                bandera.jugador = None

        # 2. TOMAR DEL SUELO
        if bandera.jugador == None and jugador.getrect().colliderect(bandera.getrect()):
            bandera.jugador = jugador.nombre
            if jugador == p_local:
                puntuacion[mi_id - 1] += 1

        # 3. TRANSPORTAR
        if bandera.jugador == jugador.nombre:
            bandera.x = jugador.x + 20
            bandera.y = jugador.y

            # 4. COLISIÓN CON SU CASA (Aquí es donde activamos el tiempo)
            if jugador.casa.getrect().colliderect(jugador.getrect()):
                bandera.x = jugador.casa.x + 7
                bandera.y = jugador.casa.y + 7
                bandera.jugador = jugador.casa
                bandera.tiempo = time.time()  # <--- SE PONE AQUÍ

        # 5. LÓGICA DE PUNTUACIÓN (2 segundos)
        if bandera.jugador == jugador.casa:
            if bandera.esperando is False:
                bandera.tiempo = time.time()
                bandera.esperando = True

            if time.time() - bandera.tiempo >= 2:
                if jugador == p_local:
                    puntuacion[mi_id - 1] += 4
                    rondas[mi_id - 1] += 1

                reiniciar()
                bandera.esperando = False
                break

def reiniciar():#Situa cada objeto como al inicio de la partida
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
    bandera.esperando = False

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
    casa1=casa(screen,0,0,"imagen/cabañapaja.png")
    p1=jugador(screen,25,35,casa1,'imagen/p1.png',"Jugador1")
    casa2=casa(screen,1210,0,"imagen/cabañapaja.png")
    p2=jugador(screen,1232,35,casa2,'imagen/p2.png',"Jugador2")
    casa3=casa(screen,0,650,"imagen/cabañapaja.png")
    p3=jugador(screen,25,685,casa3,'imagen/p3.png',"Jugador3")
    casa4=casa(screen,1210,650,"imagen/cabañapaja.png")
    p4=jugador(screen,1230,685,casa4,'imagen/p4.png',"Jugador4")
    inicio = time.time();
    #ZONA 1 (Arriba-Izquierda) | Rango X: 100-540, Y: 100-260
    muro11 = muro(screen, 150, 100, 150, 30,"imagen/muro3.jpg")  # Barra horizontal superior
    muro12 = muro(screen, 400, 100, 30, 120,"imagen/muro3.jpg")  # Barra vertical derecha
    muro13 = muro(screen, 150, 200, 100, 30,"imagen/muro3.jpg")  # Barra horizontal inferior
    muro14 = muro(screen, 300, 160, 40, 40,"imagen/muro3.jpg")  # Bloque central

    #ZONA 2 (Arriba-Derecha) | Rango X: 740-1180, Y: 100-260
    muro21 = muro(screen, 940, 100, 150, 30,"imagen/muro3.jpg")
    muro22 = muro(screen, 800, 100, 30, 120,"imagen/muro3.jpg")
    muro23 = muro(screen, 940, 200, 100, 30,"imagen/muro3.jpg")
    muro24 = muro(screen, 880, 160, 40, 40,"imagen/muro3.jpg")

    #ZONA 3 (Abajo-Izquierda) | Rango X: 100-540, Y: 460-620
    muro31 = muro(screen, 150, 590, 150, 30,"imagen/muro3.jpg")
    muro32 = muro(screen, 400, 460, 30, 120,"imagen/muro3.jpg")
    muro33 = muro(screen, 150, 460, 100, 30,"imagen/muro3.jpg")
    muro34 = muro(screen, 300, 520, 40, 40,"imagen/muro3.jpg")

    #ZONA 4 (Abajo-Derecha) | Rango X: 740-1180, Y: 460-620
    muro41 = muro(screen, 940, 590, 150, 30,"imagen/muro3.jpg")
    muro42 = muro(screen, 800, 460, 30, 120,"imagen/muro3.jpg")
    muro43 = muro(screen, 940, 460, 100, 30,"imagen/muro3.jpg")
    muro44 = muro(screen, 880, 520, 40, 40,"imagen/muro3.jpg")
    bandera=bandera(screen,"imagen/ikurrina2.png")
    muros=[muro11,muro12,muro13,muro14,muro21,muro22,muro23,muro24,muro31,muro32,muro33,muro34,muro41,muro42,muro43,muro44]
    casas=[casa1,casa2,casa3,casa4]
    jugadores=[p1,p2,p3,p4]
    velocidad=4;
    pillado=False
    p_local = jugadores[mi_id-1]
    puntuacion=[0,0,0,0]
    rondas = [0,0,0,0]

    # BUCLE PRINCIPAL
    rondas_viejas = [0, 0, 0, 0]

    # BUCLE PRINCIPAL
    while True:

        screen.blit(fondo, (0, 0))

        # 1. ENVIAR Y RECIBIR DATOS
        state = envioPosicion(p_local.x, p_local.y)

        if state:
            # SINCRONIZACIÓN CRÍTICA: Copiamos lo que dice el servidor para TODOS
            # Esto permite que tu cliente "vea" que el Jugador 2 ha llegado a 3
            puntuacion = list(state['puntuacion'])
            rondas = list(state['rondas'])

            # 2. DETECTAR PUNTO PARA REINICIAR
            if sum(state['rondas']) > sum(rondas_viejas):
                reiniciar()
            rondas_viejas = list(state['rondas'])

            # 3. ACTUALIZAR POSICIONES DE OTROS
            for p_id_str, pdata in state['players'].items():
                p_id = int(p_id_str)
                if p_id != mi_id:
                    idx = p_id - 1
                    if 0 <= idx < len(jugadores):
                        jugadores[idx].x = pdata['x']
                        jugadores[idx].y = pdata['y']
        # 5. LÓGICA DE MOVIMIENTO Y DIBUJO
        with lock:
            dibujar()
            contador()

            keys = pygame.key.get_pressed()
            p_local.old_x, p_local.old_y = p_local.x, p_local.y
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: p_local.x -= velocidad
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: p_local.x += velocidad
            if keys[pygame.K_UP] or keys[pygame.K_w]: p_local.y -= velocidad
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: p_local.y += velocidad

            colisiones(p_local)
            estadobandera()

        # 6. VERIFICAR FINAL
        try:
            finPartida()
        except Exception as e:
            pass

        # 7. EVENTOS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                client.close()
                exit()

        pygame.display.update()
        clock.tick(60)