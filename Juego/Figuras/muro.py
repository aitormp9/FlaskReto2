import pygame
import random
#Creacion del muro
class muro:
    def __init__(self, screen, x, y,ancho ,alto,imagen):
        self.screen = screen
        self.imagen = pygame.image.load(imagen)
        self.ancho = ancho
        self.alto = alto
        self.imagen = pygame.transform.scale(self.imagen, (self.ancho, self.alto))

        # Posición aleatoria
        self.x = x
        self.y = y
    #Funcion para dibujar el muro
    def draw(self):
        # Dibujar la imagen en la pantalla
        self.screen.blit(self.imagen, (self.x, self.y))
        #pygame.draw.rect(self.screen,(255,255,255),(self.x, self.y, self.ancho, self.alto))
    #Para obtener el hitbox del muro
    def getrect(self):
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)
