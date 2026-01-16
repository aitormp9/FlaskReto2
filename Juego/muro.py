import pygame
import random

class muro:
    def __init__(self, screen, x, y,ancho ,alto):
        self.screen = screen
        self.imagen = pygame.image.load("imagen/muro3.jpg")
        self.ancho = ancho
        self.alto = alto
        self.imagen = pygame.transform.scale(self.imagen, (self.ancho, self.alto))

        # Posición aleatoria
        self.x = x
        self.y = y

    def draw(self):
        # Dibujar la imagen en la pantalla
        self.screen.blit(self.imagen, (self.x, self.y))
        #pygame.draw.rect(self.screen,(255,255,255),(self.x, self.y, self.ancho, self.alto))

    def getrect(self):
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)
