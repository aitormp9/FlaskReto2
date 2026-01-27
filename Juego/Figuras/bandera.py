import pygame

class bandera:
    def __init__(self,screen,imagen):
        self.x=640
        self.y=360
        self.ancho=20
        self.alto=20
        self.screen=screen
        self.color="brown"
        self.jugador=None
        self.tiempo=0
        self.esperando=False
        self.image = pygame.image.load(imagen).convert_alpha()
        self.imagen = pygame.transform.scale(self.image, (self.ancho , self.alto ))
    def draw(self):
        #pygame.draw.rect(self.screen,self.color,(self.x,self.y,self.ancho,self.alto))
        self.screen.blit(self.imagen, (self.x, self.y))
    def getrect(self):
        return pygame.Rect(self.x,self.y,self.ancho,self.alto)
    def getestado(self):
        return self.jugador