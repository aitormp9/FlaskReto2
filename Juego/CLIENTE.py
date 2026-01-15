import pygame, socket, threading
from bandera import bandera as ClaseBandera


def check_colisiones(n_pos, v_pos, muros):
    rj = pygame.Rect(n_pos[0], n_pos[1], 20, 20)
    for m in muros:
        if rj.colliderect(m): return v_pos
    if n_pos[0] < 0 or n_pos[0] > 1260 or n_pos[1] < 0 or n_pos[1] > 700: return v_pos
    return n_pos


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 65432))

mensaje = ""
while mensaje.count("#") < 3:
    mensaje += s.recv(4096).decode()

partes = mensaje.split("#")
mi_pos = [int(x) for x in partes[0].split(":")[1].split(",")]
lista_muros = [pygame.Rect(int(v.split(",")[0]), int(v.split(",")[1]), int(v.split(",")[2]), int(v.split(",")[3])) for v
               in partes[1].split("|") if v]
lista_casas = [pygame.Rect(int(v.split(",")[0]), int(v.split(",")[1]), 70, 70) for v in partes[2].split("|") if v]
mi_id = partes[3].strip()

pygame.init()
ventana = pygame.display.set_mode((1280, 720))
b_obj = ClaseBandera(ventana)
datos_otros = {}


def recibir():
    global datos_otros, mi_pos
    while True:
        try:
            data = s.recv(2048).decode().strip()
            if not data: continue
            for msg in data.split('\n'):
                for p in msg.split('|'):
                    if ':' not in p: continue
                    idx, contenido = p.split(':')
                    val = contenido.split(',')
                    if idx == 'B':
                        b_obj.x, b_obj.y = int(val[0]), int(val[1])
                    else:
                        # Guardamos x, y, r, g, b
                        datos_otros[idx] = [int(x) for x in val]
                        if idx == mi_id:
                            mi_pos = [int(val[0]), int(val[1])]
        except:
            break


threading.Thread(target=recibir, daemon=True).start()

clock = pygame.time.Clock()
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT: exit()

    old = mi_pos[:]
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]: mi_pos[0] -= 5
    if keys[pygame.K_d]: mi_pos[0] += 5
    if keys[pygame.K_w]: mi_pos[1] -= 5
    if keys[pygame.K_s]: mi_pos[1] += 5

    mi_pos = check_colisiones(mi_pos, old, lista_muros)
    try:
        s.send(f"{mi_pos[0]},{mi_pos[1]}\n".encode())
    except:
        break

    ventana.fill((30, 30, 30))
    for m in lista_muros: pygame.draw.rect(ventana, (100, 100, 100), m)
    for c in lista_casas: pygame.draw.rect(ventana, (200, 200, 0), c, 2)

    b_obj.draw()

    for id_j, d in list(datos_otros.items()):
        if len(d) >= 5:  # Jugador con color
            pygame.draw.circle(ventana, (d[2], d[3], d[4]), (d[0] + 10, d[1] + 10), 12)
            if id_j == mi_id:
                pygame.draw.circle(ventana, (255, 255, 255), (d[0] + 10, d[1] + 10), 14, 2)

    pygame.display.flip()
    clock.tick(60)