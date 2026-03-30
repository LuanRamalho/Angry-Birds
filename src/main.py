import pygame
import math
import os
import sys
from level import Level
from characters import Bird, Pig

# --- Configurações do Motor ---
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1200, 600
FPS = 60
GRAVITY = 0.25
GROUND_Y = HEIGHT - 60
VEL_QUEDA_BLOCO = 6  # Velocidade da madeira caindo

# Caminhos de recursos (ajustado para rodar da pasta /src)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, "resources", "images")
SOUNDS_DIR = os.path.join(BASE_DIR, "resources", "sounds")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Angry Birds Full-Stack Edition")
clock = pygame.time.Clock()

assets = {'images': {}, 'sounds': {}}

def load_all_assets():
    image_map = {
        'bird': 'red-bird.png',
        'pig': 'pig_failed.png',
        'sling': 'sling.png',
        'bg': 'background.png',
        'wood': 'wood.png'
    }
    for key, filename in image_map.items():
        path = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            if key == 'bird': img = pygame.transform.scale(img, (35, 35))
            if key == 'pig': img = pygame.transform.scale(img, (40, 40))
            if key == 'bg': img = pygame.transform.scale(img, (WIDTH, HEIGHT))
            assets['images'][key] = img
            
    sound_path = os.path.join(SOUNDS_DIR, "angry-birds.ogg")
    if os.path.exists(sound_path):
        assets['sounds']['theme'] = pygame.mixer.Sound(sound_path)

class GameBird(Bird):
    def __init__(self, x, y):
        super().__init__(x, y, assets['images'])
        
    def update(self):
        if self.is_flying:
            self.vel.y += GRAVITY
            self.pos += self.vel
            # Reset se sair da tela ou bater no chão
            if self.pos.y > GROUND_Y or self.pos.x > WIDTH or self.pos.x < 0:
                self.reset()

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.pos.x - 17, self.pos.y - 17))

def main():
    load_all_assets()
    if assets['sounds'].get('theme'):
        assets['sounds']['theme'].play(-1)

    # Containers de objetos da fase
    pigs, columns, beams = [], [], []
    
    lvl_manager = Level(pigs, columns, beams, None)
    lvl_manager.number = 0
    lvl_manager.load_level() 

    bird = GameBird(180, 430)
    
    running = True
    while running:
        # --- 1. Renderização do Fundo ---
        if assets['images'].get('bg'):
            screen.blit(assets['images']['bg'], (0, 0))
        else:
            screen.fill((135, 206, 235))

        pygame.draw.rect(screen, (34, 139, 34), (0, GROUND_Y, WIDTH, 60))
        if assets['images'].get('sling'):
            screen.blit(assets['images']['sling'], (150, 410))

        # --- 2. Lógica de Vitória / Próxima Fase ---
        pigs_vivos = [p for p in pigs if p.active]
        if len(pigs_vivos) == 0:
            pygame.display.flip()
            pygame.time.delay(1200) # Pausa dramática
            pigs.clear()
            columns.clear()
            beams.clear()
            lvl_manager.number += 1
            lvl_manager.load_level()
            bird.reset()

        # --- 3. Input e Estilingue ---
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not bird.is_flying and bird.pos.distance_to(mouse_pos) < 50:
                    bird.is_dragged = True
            if event.type == pygame.MOUSEBUTTONUP:
                if bird.is_dragged:
                    bird.is_dragged = False
                    bird.is_flying = True
                    # Força ajustada para 0.22 para alcançar porcos distantes
                    bird.vel = (bird.origin - bird.pos) * 0.22

        if bird.is_dragged:
            dist = bird.origin.distance_to(mouse_pos)
            if dist > 90:
                bird.pos = bird.origin + (mouse_pos - bird.origin).normalize() * 90
            else:
                bird.pos = mouse_pos
            pygame.draw.line(screen, (50, 20, 0), bird.origin, bird.pos, 3)

        bird.update()
        bird_rect = pygame.Rect(bird.pos.x - 15, bird.pos.y - 15, 30, 30)

        # --- 4. Colisão e Física de Destruição ---
        todos_blocos = columns + beams
        
        for bloco in todos_blocos:
            # Sincroniza o Rect de colisão com a posição atual (Physics -> Screen)
            draw_y = GROUND_Y - bloco.pos.y - bloco.height
            bloco_rect = pygame.Rect(bloco.pos.x, draw_y, bloco.width, bloco.height)

            # A) Colisão Pássaro -> Madeira
            if bird.is_flying and bird_rect.colliderect(bloco_rect):
                if not hasattr(bloco, 'is_falling'): bloco.is_falling = True
                bloco.is_falling = True
                bird.vel *= 0.5 # Perde força ao atravessar madeira

            # B) Física da Madeira Caindo
            if getattr(bloco, 'is_falling', False):
                bloco.pos.y -= VEL_QUEDA_BLOCO
                if bloco.pos.y <= 0:
                    bloco.pos.y = 0
                    bloco.is_falling = False
                
                # C) Madeira Caindo -> Mata Porco
                for pig in pigs:
                    if pig.active:
                        pig_draw_y = GROUND_Y - pig.pos.y - 35
                        pig_rect = pygame.Rect(pig.pos.x - 15, pig_draw_y, 30, 30)
                        if bloco_rect.colliderect(pig_rect):
                            pig.active = False # Esmagado!

        # D) Colisão Direta Pássaro -> Porco
        for pig in pigs:
            if pig.active:
                adj_pig_pos = pygame.Vector2(pig.pos.x, GROUND_Y - pig.pos.y - 20)
                if bird.is_flying and bird.pos.distance_to(adj_pig_pos) < 35:
                    pig.active = False

        # --- 5. Desenho dos Elementos ---
        for col in columns: col.draw(screen, assets['images'].get('wood'), HEIGHT)
        for beam in beams: beam.draw(screen, assets['images'].get('wood'), HEIGHT)
        
        for pig in pigs:
            if pig.active:
                # O Y aqui segue a mesma lógica da colisão: GROUND_Y - pos.y
                draw_y = GROUND_Y - pig.pos.y - 40
                screen.blit(assets['images']['pig'], (pig.pos.x - 20, draw_y))

        bird.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
