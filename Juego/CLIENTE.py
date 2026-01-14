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

pygame.init()
screen = pygame.display.set_mode((1280, 720))
imagen=pygame.image.load('imagen/fondo.jpg')
fondo=pygame.transform.scale(imagen,(1280,720))
clock = pygame.time.Clock()
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

    screen.blit(fondo, (0, 0))  # fondo negro

    # Dibujar jugadores
    for p in state['players'].values():
        pygame.draw.rect(screen, (255, 0, 0), (p['x'], p['y'], 30, 30))

    # Dibujar bandera
    f = state['flag']
    color_flag = (0, 255, 0) if f['estado'] is None else (255, 255, 0)
    pygame.draw.rect(screen, color_flag, (f['x'], f['y'], 20, 20))

    pygame.display.update()

pygame.quit()
client.close()
