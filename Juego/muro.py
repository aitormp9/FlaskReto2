import pygame
import random

class muro:
    def __init__(self, screen, x, y, finx, finy):
        self.screen = screen
        self.imagen = pygame.image.load("imagen/muro2.jpg")
        self.ancho = random.randint(10, 150)
        self.alto = random.randint(10, 200)
        #self.imagen = pygame.transform.scale(self.imagen, (self.ancho, self.alto))

        # Posición aleatoria
        self.x = random.randint(x, finx)
        self.y = random.randint(y, finy)

        # Ajustar posición si sale del borde
        if self.x < 50:
            self.x += 50
        if self.y < 50:
            self.y += 50
        if self.x + self.ancho > 1180:
            self.x = 1180 - self.ancho
        if self.y + self.alto > 620:
            self.y = 620 - self.alto

    def draw(self):
        # Dibujar la imagen en la pantalla
        #self.screen.blit(self.imagen, (self.x, self.y))
        pygame.draw.rect(self.screen,(255,255,255),(self.x, self.y, self.ancho, self.alto))

    def getrect(self):
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)
