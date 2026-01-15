import pygame, socket, threading
from bandera import bandera as DibujoBandera

# --- CONEXIÓN ---
s = socket.socket()
s.connect(('localhost', 65432))

datos_inicio = s.recv(4096).decode()
partes = datos_inicio.split("#")
mi_pos = [int(n) for n in partes[0].split(":")[1].split(",")]
muros = [pygame.Rect(int(x), int(y), int(w), int(h)) for m in partes[1].split("|") for x, y, w, h in [m.split(",")]]
mi_id = partes[3].strip()

# --- INICIO PYGAME ---
pygame.init()
ventana = pygame.display.set_mode((1280, 720))
fuente = pygame.font.SysFont("Arial", 25, bold=True)
la_bandera = DibujoBandera(ventana)
pos_texto_casas = [[25, 25], [1235, 25], [25, 675], [1235, 675]]
casas_pos = [[0, 0], [1210, 0], [0, 650], [1210, 650]]
# Variables de estado
otros_jugadores = {}
score_global = [0, 0, 0, 0]


def recibir():
    global otros_jugadores, mi_pos, score_global
    while True:
        try:
            data = s.recv(4096).decode().strip()
            if not data: continue
            for mensaje in data.split('\n'):
                temp_jugadores = {}
                for item in mensaje.split('|'):
                    if ':' not in item: continue
                    clave, valor = item.split(':')

                    if clave == 'B':  # Bandera
                        b_pos = [int(n) for n in valor.split(',')]
                        la_bandera.x, la_bandera.y = b_pos[0], b_pos[1]
                    elif clave == 'S':  # Scores
                        score_global = [int(n) for n in valor.split(',')]
                    else:  # Jugadores
                        v = [int(n) for n in valor.split(',')]
                        temp_jugadores[clave] = v
                        if clave == mi_id:
                            if abs(mi_pos[0] - v[0]) > 50:
                                mi_pos[0], mi_pos[1] = v[0], v[1]
                otros_jugadores = temp_jugadores
        except:
            break


threading.Thread(target=recibir, daemon=True).start()

reloj = pygame.time.Clock()
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT: exit()

    # Control y colisiones
    teclas = pygame.key.get_pressed()
    vieja_pos = mi_pos[:]
    if teclas[pygame.K_a]: mi_pos[0] -= 5
    if teclas[pygame.K_d]: mi_pos[0] += 5
    if teclas[pygame.K_w]: mi_pos[1] -= 5
    if teclas[pygame.K_s]: mi_pos[1] += 5

    mi_pos[0] = max(0, min(1260, mi_pos[0]))
    mi_pos[1] = max(0, min(700, mi_pos[1]))

    rect_yo = pygame.Rect(mi_pos[0], mi_pos[1], 20, 20)
    for m in muros:
        if rect_yo.colliderect(m): mi_pos = vieja_pos

    try:
        s.send(f"{mi_pos[0]},{mi_pos[1]}\n".encode())
    except:
        break

    # --- DIBUJAR ---
    ventana.fill((30, 30, 30))
    for m in muros: pygame.draw.rect(ventana, (100, 100, 100), m)
    la_bandera.draw()

    # Dibujar Marcador
    for i in range(4):
        txt = fuente.render(f" {score_global[i]}", False, (255, 255, 255))
        ventana.blit(txt, (pos_texto_casas[i][0], pos_texto_casas[i][1]))
    #Dibujar Casa
    for i in range(4):
        # Dibujamos un cuadrado de 70x70 en cada esquina
        # Usamos el color de cada jugador para saber cuál es cuál
        pos_casa = casas_pos[i]
        pygame.draw.rect(ventana, (255,255,255), (pos_casa[0], pos_casa[1], 70, 70),
                         2)  # El '2' es para que solo sea el borde
        # Dibujar Jugadores
    for id_j, d in otros_jugadores.items():
        if len(d) >= 5:
            color = (d[2], d[3], d[4])
            pygame.draw.circle(ventana, color, (d[0] + 10, d[1] + 10), 10)
            if id_j == mi_id:
                pygame.draw.circle(ventana, (255, 255, 255), (d[0] + 10, d[1] + 10), 13, 2)

    pygame.display.flip()
    reloj.tick(60)