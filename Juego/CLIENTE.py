import pygame
import socket
import threading


# --- FUNCIÓN DE COLISIONES (Copiada aquí para no importar el server) ---
def check_colisiones(nueva_pos, vieja_pos, muros):
    nx, ny = nueva_pos
    rect_jugador = pygame.Rect(nx, ny, 20, 20)  # 20x20 como tus dibujos

    # Bordes pantalla
    if nx < 0 or nx > 1260 or ny < 0 or ny > 700:
        return vieja_pos

    # Muros
    for muro in muros:
        if rect_jugador.colliderect(muro):
            return vieja_pos
    return [nx, ny]


# --- RED ---
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 65432))

lista_muros_rects = []
mi_pos = [0, 0]  # Valor inicial por defecto
lista_casas=[]
bandera_rect="";
d=0;
# Recibir configuración inicial (START)
# Aumentamos el buffer a 4096 porque el mapa es grande
# Sustituye la línea: mensaje = s.recv(8192).decode('utf-8') por esto:
mensaje = ""
while mensaje.count("#") < 3: mensaje += s.recv(4096).decode('utf-8')

if mensaje.startswith("START:"):
    # Separamos las 3 partes
    partes = mensaje.split("#")
    parte_jugador = partes[0]
    parte_muros = partes[1]
    parte_casas = partes[2]
    parte_bandera=partes[3]

    # 1. Posición inicial
    mi_pos = [int(x) for x in parte_jugador.split(":")[1].split(",")]

    # 2. Muros
    lista_muros_rects = []
    for m in parte_muros.split("|"):
        d = [int(v) for v in m.split(",")]
        lista_muros_rects.append(pygame.Rect(d[0], d[1], d[2], d[3]))

    # 3. Casas (CORREGIDO)
    lista_casas = []
    for c in parte_casas.split("|"):
        d = [int(v) for v in c.split(",")] # Usamos 'c', que es el texto de la casa
        lista_casas.append(pygame.Rect(d[0], d[1], 50, 50)) # Tamaño 70x70 o el que prefieras
    limpio = parte_bandera.replace("[", "").replace("]", "").replace("'", "").strip()
    d = [int(v) for v in limpio.split(",")]
    bandera_rect = pygame.Rect(d[0], d[1], 15, 15)
otros_jugadores = {}


def recibir_datos():
    global otros_jugadores
    while True:
        try:
            data = s.recv(1024).decode('utf-8')
            if data and ":" in data:
                nuevo_estado = {}
                for p in data.split('|'):
                    if ":" in p:
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
velocidad = 3

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); exit()

    # 1. Guardamos posición actual como "vieja"
    pos_anterior = mi_pos[:]
    nx, ny = mi_pos[0], mi_pos[1]

    # 2. Calculamos NUEVA posición tentativa
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:  nx -= velocidad
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: nx += velocidad
    if keys[pygame.K_UP] or keys[pygame.K_w]:    ny -= velocidad
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:  ny += velocidad

    # 3. Validamos la nueva posición con la función de colisiones
    mi_pos = check_colisiones([nx, ny], pos_anterior, lista_muros_rects)

    # 4. Enviamos posición validada al servidor
    try:
        s.sendall(f"{mi_pos[0]},{mi_pos[1]}".encode('utf-8'))
    except:
        break

    # --- DIBUJAR ---
    ventana.fill((0, 0, 0))

    # Dibujar muros
    for m in lista_muros_rects:
        pygame.draw.rect(ventana, (100, 100, 100), m, border_radius=2)

    # Dibujar todos los jugadores (el servidor nos manda a todos, incluyéndonos)
    for id_jug, pos in otros_jugadores.items():
        # Si la posición es la mía, me pinto de azul, si no, de blanco
        color = (0, 150, 255) if [pos[0], pos[1]] == mi_pos else (255, 255, 255)
        pygame.draw.rect(ventana, color, (pos[0], pos[1], 20, 20), border_radius=8)
    for casa in lista_casas:
        pygame.draw.rect(ventana, (255, 255, 0), casa)
    pygame.draw.rect(ventana,(0,255,255),bandera_rect)

    pygame.display.flip()
    reloj.tick(60)