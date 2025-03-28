import random
import pygame
# from models.enemy import Enemy
# from models.player import Player_Character
# from models.bullet import Bullet
from models.asset_system import AssetsSystem
import json

pygame.init()

# Set up the drawing window
WIDTH = 500
HEIGHT = 500
SCALE = 2
TILE_SIZE = 16
# draw everything on the screen, then scale it to the desired size
display = pygame.display.set_mode((WIDTH*SCALE, HEIGHT*SCALE), pygame.RESIZABLE)
screen = pygame.Surface((WIDTH, HEIGHT))
pygame.display.set_caption('Space Editor')

clock = pygame.time.Clock()

running = True

# Game objects
enemies: list[Enemy] = []
with open("map.json", 'r') as file:
            level = json.loads(file.read())
            for elementKey in level:
                cords = elementKey.split(";")
                x = int(cords[0])
                y = int(cords[1]) 
                enemies.append(Enemy(x*TILE_SIZE, y*TILE_SIZE,screen))



bg1 = pygame.image.load('assets/bg1.png')
bg2 = pygame.image.load('assets/bg2.png')
bg3 = pygame.image.load('assets/bg3.png')

bg1 = pygame.transform.scale(bg1, (WIDTH, HEIGHT))
bg2 = pygame.transform.scale(bg2, (WIDTH, HEIGHT))
bg3 = pygame.transform.scale(bg3, (WIDTH, HEIGHT))

while running:
    # draw bgs
    screen.fill((0, 0, 0))
    screen.blit(bg3, (0, 0))
    screen.blit(bg1, (0, 0))
    screen.blit(bg2, (0, 0))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_s] and keys[pygame.K_LCTRL]:
                with open("map.json", 'w') as file:
                    json.dump([f"{enemy.rect.x//TILE_SIZE};{enemy.rect.y//TILE_SIZE}" for enemy in enemies], file)
                  
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: # left click
                pos = pygame.mouse.get_pos()
                grid_pos = (pos[0] // (SCALE * TILE_SIZE), pos[1] // (SCALE * TILE_SIZE)) # from mouse click to grid position
                real_pos = (grid_pos[0] * TILE_SIZE, grid_pos[1] * TILE_SIZE)  # from grid position to ui position
                for enemy in enemies.copy():
                    if enemy.rect.collidepoint(real_pos):
                        print("Enemy removed")
                        enemies.remove(enemy)
                        break
                else:
                    enemies.append(Enemy(real_pos[0], real_pos[1], screen))

    # Debugging
    for enemy in enemies: # updating enemies
        enemy.update(0.1)

    [pygame.draw.rect(screen, (0, 255, 0), enemy.rect, 1) for enemy in enemies] # draw enemy rects 

    for x in range(0, WIDTH, TILE_SIZE): # drawing grid
        for y in range(0, HEIGHT, TILE_SIZE):
            pygame.draw.rect( display, (255, 255, 255), (x, y, TILE_SIZE, TILE_SIZE), 1)

    # resetting lists
    bullets_to_remove = []
    enemies_to_remove = []


    display.blit(pygame.transform.scale(screen, (display.get_width(), display.get_height())), (0, 0))
    pygame.display.flip()
    delta_time = max(0.001, min(0.1, clock.tick(60) / 1000))

pygame.quit()
