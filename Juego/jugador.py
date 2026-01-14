import pygame

class jugador:
    def __init__(self,screen,x,y,casa,imagen):
        #self.nombre=nombre
        self.screen=screen
        self.altura=20
        self.anchura=20
        self.borde=10
        self.x=x
        self.y=y
        self.casa=casa
        self.xinicio=x
        self.yinicio=y
        #self.imagennombre==pygame.image.load(imagen)
        #self.imagen = pygame.transform.scale(self.imagennombre, (self.anchura , self.altura ))

    def draw(self):
        #self.screen.blit(self.imagen, (self.x, self.y))
        pygame.draw.rect(self.screen,(0, 0, 0),(self.x, self.y, self.anchura, self.altura),border_radius=8)

    def getrect(self):
        return pygame.Rect(self.x,self.y,self.anchura,self.altura)