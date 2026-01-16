import pygame

class bandera:
    def __init__(self,screen):
        self.x=640
        self.y=360
        self.ancho=15
        self.alto=15
        self.screen=screen
        self.color="brown"
        self.jugador=None
        self.tiempo=0
        self.esperando=False
    def draw(self):
        pygame.draw.rect(self.screen,self.color,(self.x,self.y,self.ancho,self.alto))
    def getrect(self):
        return pygame.Rect(self.x,self.y,self.ancho,self.alto)
    def getestado(self):
        return self.jugador