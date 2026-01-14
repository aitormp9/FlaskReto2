import socket
import pickle
import pygame
import sys

HOST = '192.168.25.46'
PORT = 2000
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
vel = 5

# Identificador del jugador (podrías recibirlo del servidor)
player_id = str(client.getsockname())

# Posición inicial
player = {"x": 25, "y": 25}
players = {}
flag = {"x": 640, "y": 360, "estado": None}

def send_position():
    try:
        client.sendall(pickle.dumps(player))
        state = pickle.loads(client.recv(4096))
        return state
    except Exception as e:
        print("Error:", e)
        return None

run = True
while run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]: player["x"] -= vel
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player["x"] += vel
    if keys[pygame.K_UP] or keys[pygame.K_w]: player["y"] -= vel
    if keys[pygame.K_DOWN] or keys[pygame.K_s]: player["y"] += vel

    # Enviar posición y recibir estado
    state = send_position()
    if state:
        players = state["players"]
        flag = state["flag"]

    # Dibujar
    screen.fill((0,0,0))
    for pid, pdata in players.items():
        color = (0,255,0) if pid == player_id else (255,0,0)
        pygame.draw.rect(screen, color, (pdata["x"], pdata["y"], 30, 30))

    f_color = (255,255,0) if flag["estado"] else (0,255,0)
    pygame.draw.rect(screen, f_color, (flag["x"], flag["y"], 20, 20))

    pygame.display.update()

pygame.quit()
client.close()
sys.exit()
