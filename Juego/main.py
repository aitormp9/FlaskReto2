import pygame
import time
import random
from jugador import jugador
from casa import casa
from muro import muro
from bandera import bandera
import socket
import pickle


pygame.init()
screen = pygame.display.set_mode((1280, 720))
imagen=pygame.image.load('imagen/fondo.jpg')
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
muro11=muro(screen,100,100,540,260)#1.1
muro12=muro(screen,100,100,540,260)#1.2
muro13=muro(screen,100,100,540,260)#1.3
muro14=muro(screen,100,100,540,260)#1.4

muro21=muro(screen,740,100,1180,260)#2.1
muro22=muro(screen,740,100,1180,260)#2.2
muro23=muro(screen,740,100,1180,260)#2.3
muro24=muro(screen,740,100,1180,260)#2.4

muro31=muro(screen,100,460,540,620)#3.1
muro32=muro(screen,100,460,540,620)#3.2
muro33=muro(screen,100,460,540,620)#3.3
muro34=muro(screen,100,460,540,620)#3.4

muro41=muro(screen,740,460,1180,620)#4.1
muro42=muro(screen,740,460,1180,620)#4.2
muro43=muro(screen,740,460,1180,620)#4.3
muro44=muro(screen,740,460,1180,620)#4.4
bandera=bandera(screen)
jugadores=[]
muros=[]
casas=[]
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
casas.append(casa1)
casas.append(casa2)
casas.append(casa3)
casas.append(casa4)
velocidad=2;
pillado=False

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
            if bandera.esperando is False:
                bandera.tiempo = time.time()
                bandera.esperando=True
            if time.time() - bandera.tiempo >= 2:
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
while True:
    screen.blit(fondo, (0, 0))
    dibujar()

    # Guardar posiciones anteriores (para colisiones/animaciones)
    for player in jugadores:
        player.old_x = player.x
        player.old_y = player.y

    # --- Eventos ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit() # cerramos conexión al servidor
            exit()

    # --- Movimiento del jugador local (p1) ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        p1.x -= velocidad
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        p1.x += velocidad
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        p1.y -= velocidad
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        p1.y += velocidad


        colisiones(player)
    estadobandera()

    pygame.display.update()
    clock.tick(60)
