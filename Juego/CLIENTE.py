import pygame
import socket
import pickle
import sys

# --- Configuración ---
HOST = '192.168.25.46'  # IP del servidor
PORT = 2000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# --- Pygame ---
pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Cliente Captura la Bandera")
clock = pygame.time.Clock()
vel = 5

# Jugador local
player = {"x": 100, "y": 100}
# Estado completo recibido del servidor
players = {}
flag = {"x": 640, "y": 360, "estado": None}

# --- Función enviar posición ---
def send_position():
    try:
        client.sendall(pickle.dumps(player))
        state = pickle.loads(client.recv(4096))
        return state
    except Exception as e:
        print("Error:", e)
        return None

# --- Bucle principal ---
run = True
while run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Movimiento del jugador
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

    # --- Dibujar ---
    screen.fill((0, 0, 0))  # fondo negro
    # Dibujar jugadores
    for pid, pdata in players.items():
        color = (0,255,0) if pid == str(client.getsockname()) else (255,0,0)
        pygame.draw.rect(screen, color, (pdata["x"], pdata["y"], 30, 30))
    # Dibujar bandera
    f_color = (255,255,0) if flag["estado"] else (0,255,0)
    pygame.draw.rect(screen, f_color, (flag["x"], flag["y"], 20, 20))

    pygame.display.update()

pygame.quit()
client.close()
sys.exit()
