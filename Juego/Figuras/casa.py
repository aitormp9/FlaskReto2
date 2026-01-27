import pygame

class casa:
    def __init__(self,screen,x,y,imagen):
        self.screen=screen
        self.x=x
        self.y=y
        self.color=(255,255,255)
        self.ancho=50
        self.alto=50
        self.image=pygame.image.load(imagen).convert_alpha()
        self.imagen = pygame.transform.scale(self.image, (self.ancho+15, self.alto+15))

    def draw(self):
        self.screen.blit(self.imagen, (self.x, self.y))

    def getrect(self):
        return pygame.Rect(self.x,self.y,self.ancho,self.alto)