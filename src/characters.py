import pygame

class Bird():
    def __init__(self, x, y, assets):
        self.life = 20
        self.pos = pygame.Vector2(x, y)
        self.origin = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.is_flying = False
        self.is_dragged = False
        self.radius = 12
        self.image = assets.get('bird')

    def reset(self):
        self.pos = pygame.Vector2(self.origin.x, self.origin.y)
        self.vel = pygame.Vector2(0, 0)
        self.is_flying = False
        self.is_dragged = False

class Pig():
    def __init__(self, x, y, space=None): # Mantive 'space' para não quebrar o level.py
        self.life = 20
        self.pos = pygame.Vector2(x, y)
        self.active = True
        self.radius = 14
