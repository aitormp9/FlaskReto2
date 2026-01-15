import socket, threading, random, pygame, time

HOST, PORT = '0.0.0.0', 65432
pos_inicios = [[25, 25], [1245, 25], [25, 685], [1246, 685]]
colores_jugadores = ["0,150,255", "255,50,50", "50,255,50", "255,200,0"]
casas_pos = [[0, 0], [1210, 0], [0, 650], [1210, 650]]
rect_casas = [pygame.Rect(p[0], p[1], 70, 70) for p in casas_pos]

def generar_muros():
    muros = []
    zonas = [(100, 100, 540, 260), (740, 100, 1180, 260), (100, 460, 540, 620), (740, 460, 1180, 620)]
    for z in zonas:
        for _ in range(4):
            muros.append(f"{random.randint(z[0], z[2])},{random.randint(z[1], z[3])},{random.randint(20, 80)},{random.randint(20, 80)}")
    return "|".join(muros)

DATOS_MUROS = generar_muros()

class ServerLogic:
    def __init__(self):
        self.bx, self.by = 640, 360
        self.jugador = None
        self.en_casa = False
        self.t_entrega = 0
        self.jugadores = {}

    def estadobandera(self):
        ahora = time.time()
        if self.en_casa:
            if ahora - self.t_entrega > 2:
                self.bx, self.by, self.jugador, self.en_casa = 640, 360, None, False
            return
        for id_j, p in list(self.jugadores.items()):
            rj = pygame.Rect(p[0], p[1], 20, 20)
            rb = pygame.Rect(self.bx, self.by, 15, 15)
            if self.jugador is not None and self.jugador != id_j and self.jugador != "CASA":
                if rj.colliderect(rb):
                    id_p = self.jugador
                    self.jugadores[id_p] = pos_inicios[id_p % 4][:]
                    self.jugador = None
            if self.jugador is None and rj.colliderect(rb):
                self.jugador = id_j
            if self.jugador == id_j:
                self.bx, self.by = p[0] + 5, p[1] + 5
                if rj.colliderect(rect_casas[id_j % 4]):
                    self.bx, self.by = casas_pos[id_j % 4][0] + 25, casas_pos[id_j % 4][1] + 25
                    self.en_casa, self.t_entrega, self.jugador = True, ahora, "CASA"

game = ServerLogic()
clientes = {}

def manejar_cliente(conn, id_j):
    game.jugadores[id_j] = pos_inicios[id_j % 4][:]
    clientes[id_j] = conn
    try:
        inicio = f"START:{game.jugadores[id_j][0]},{game.jugadores[id_j][1]}#{DATOS_MUROS}#0,0|1210,0|0,650|1210,650#{id_j}\n"
        conn.send(inicio.encode())
        while True:
            data = conn.recv(1024).decode().strip()
            if not data: break
            for msg in data.split('\n'):
                if ',' in msg:
                    try: game.jugadores[id_j] = [int(float(x)) for x in msg.split(',')]
                    except: continue
            game.estadobandera()
            p_jugs = "|".join([f"{i}:{p[0]},{p[1]},{colores_jugadores[int(i)%4]}" for i, p in game.jugadores.items()])
            paquete = f"{p_jugs}|B:{int(game.bx)},{int(game.by)}\n"
            for c in list(clientes.values()):
                try: c.send(paquete.encode())
                except: pass
    except: pass
    finally:
        if id_j in clientes: del clientes[id_j]
        if id_j in game.jugadores: del game.jugadores[id_j]
        conn.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen()
print("SERVIDOR OK")
idx = 0
while True:
    c, a = s.accept()
    threading.Thread(target=manejar_cliente, args=(c, idx), daemon=True).start()
    idx += 1