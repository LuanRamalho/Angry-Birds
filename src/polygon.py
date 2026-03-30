import pygame

class Polygon():
    def __init__(self, pos, length, height, space=None, mass=5.0):
        # pos agora é uma tupla (x, y)
        self.pos = pygame.Vector2(pos[0], pos[1])
        self.width = length
        self.height = height
        self.active = True
        
        # Criamos um Rect para colisões simples
        # Como o level.py usa coordenadas de física (Y sobe), 
        # o desenho será ajustado no main
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)

    def draw(self, screen, image, height_screen):
        if self.active:
            # Inverte o Y para desenhar corretamente no Pygame
            draw_y = height_screen - self.pos.y - self.height
            if image:
                img_scaled = pygame.transform.scale(image, (self.width, self.height))
                screen.blit(img_scaled, (self.pos.x, draw_y))
            else:
                pygame.draw.rect(screen, (139, 69, 19), (self.pos.x, draw_y, self.width, self.height))
