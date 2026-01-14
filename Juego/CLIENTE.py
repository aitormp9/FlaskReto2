import random

import pygame
import socket
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 65432))

# --- NUEVO: ESPERAR POSICIÓN INICIAL ---
mensaje_bienvenida = s.recv(1024).decode('utf-8')
# El servidor manda "START:x,y"
if mensaje_bienvenida.startswith("START:"):
    pos_str = mensaje_bienvenida.split(":")[1]
    mi_pos = [int(x) for x in pos_str.split(',')]
    lista_muros_coords = []
    for m in parte_muros.split("|"):
        coords = [int(c) for c in m.split(",")]
        lista_muros_coords.append(coords)
otros_jugadores = {}


def recibir_datos():
    global otros_jugadores
    while True:
        try:
            data = s.recv(1024).decode('utf-8')
            if data and not data.startswith("START:"):
                nuevo_estado = {}
                for p in data.split('|'):
                    id_jug, pos = p.split(':')
                    nuevo_estado[int(id_jug)] = [int(x) for x in pos.split(',')]
                otros_jugadores = nuevo_estado
        except:
            break


threading.Thread(target=recibir_datos, daemon=True).start()

# --- PYGAME ---
pygame.init()
ventana = pygame.display.set_mode((1280, 720))
reloj = pygame.time.Clock()
velocidad=2
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        mi_pos[0] -= velocidad
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        mi_pos[0] += velocidad
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        mi_pos[1] -= velocidad
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        mi_pos[1] += velocidad

    s.sendall(f"{mi_pos[0]},{mi_pos[1]}".encode('utf-8'))

    ventana.fill((0,0,0))
    for id_jug, pos in otros_jugadores.items():
        pygame.draw.rect(ventana, (255, 255,255), (pos[0], pos[1], 20, 20), border_radius=8)
    for m_pos in lista_muros_coords:
        pygame.draw.rect(ventana, (100, 100, 100), (m_pos[0], m_pos[1], ancho_muro,alto_muro), border_radius=8)
    pygame.display.flip()
    reloj.tick(60)