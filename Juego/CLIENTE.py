import pygame
import socket
import pickle
import casa
import jugador
import muro
import bandera

HOST = '192.168.25.46'
PORT = 2000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

pygame.init()
screen = pygame.display.set_mode((1280, 720))
imagen = pygame.image.load('imagen/fondo.jpg')
fondo = pygame.transform.scale(imagen, (1280, 720))

clock = pygame.time.Clock()
vel = 2
x, y = 100, 100  # posición inicial

def send_position(x, y):
    try:
        client.sendall(pickle.dumps({"x": x, "y": y}))
        state = pickle.loads(client.recv(4096))
        return state
    except Exception as e:
        print("Error al enviar/recibir:", e)
        return None

run = True
while run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: x -= vel
    if keys[pygame.K_RIGHT]: x += vel
    if keys[pygame.K_UP]: y -= vel
    if keys[pygame.K_DOWN]: y += vel

    state = send_position(x, y)
    if state is None:
        continue

    screen.blit(fondo, (0, 0))

    for p in state['players'].values():
        pygame.draw.rect(screen, (255, 0, 0), (p['x'], p['y'], 30, 30))

    f = state['flag']
    color_flag = (0, 255, 0) if f['estado'] is None else (255, 255, 0)
    pygame.draw.rect(screen, color_flag, (f['x'], f['y'], 20, 20))

    pygame.display.update()

pygame.quit()
client.close()
