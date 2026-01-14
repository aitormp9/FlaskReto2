# client.py
import pygame
import socket
import pickle

# Configuración del servidor
HOST = '192.168.25.46'  # cambia si el servidor está en otra máquina
PORT = 2000

# Conexión con el servidor
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 500, 500
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CTF Multijugador")

# Posición inicial del jugador
x, y = 50, 50
vel = 5

clock = pygame.time.Clock()

def send_position(x, y):
    """
    Envia la posición al servidor y recibe el estado completo
    """
    try:
        client.sendall(pickle.dumps({"x": x, "y": y}))
        state = pickle.loads(client.recv(4096))
        return state
    except:
        return None

run = True
while run:
    clock.tick(60)  # 60 FPS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Movimiento del jugador
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: x -= vel
    if keys[pygame.K_RIGHT]: x += vel
    if keys[pygame.K_UP]: y -= vel
    if keys[pygame.K_DOWN]: y += vel

    # Enviar posición y recibir estado del juego
    state = send_position(x, y)
    if state is None:
        continue

    win.fill((0, 0, 0))  # fondo negro

    # Dibujar jugadores
    for p in state['players'].values():
        pygame.draw.rect(win, (255, 0, 0), (p['x'], p['y'], 30, 30))

    # Dibujar bandera
    f = state['flag']
    color_flag = (0, 255, 0) if f['estado'] is None else (255, 255, 0)
    pygame.draw.rect(win, color_flag, (f['x'], f['y'], 20, 20))

    pygame.display.update()

pygame.quit()
client.close()
