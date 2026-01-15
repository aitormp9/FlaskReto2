import pygame

class BanderaServidor:
    def __init__(self):
        self.x = 640
        self.y = 360
        self.ancho = 15
        self.alto = 15
        self.jugador = None  # Cambiado a 'jugador' para coincidir con tu lógica
        self.en_casa = False
        self.tiempo_entrega = 0

    def getrect(self):
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)