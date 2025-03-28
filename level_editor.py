import random
import pygame
from asset_system import AssetsSystem
import json

from models.block import Block

pygame.init()

# Set up the drawing window
HEIGHT, WIDTH = 360,640
SCALE = 1
TILE_SIZE = 16
# draw everything on the screen, then scale it to the desired size
display = pygame.display.set_mode((WIDTH*SCALE, HEIGHT*SCALE), pygame.RESIZABLE)
screen = pygame.Surface((WIDTH, HEIGHT))
pygame.display.set_caption('Space Editor')

clock = pygame.time.Clock()

running = True

# Game objects
blocks: list[Block] = []
with open("levels/map.json", 'r') as file:
            level = json.loads(file.read())
            for elementKey in level:
                cords = elementKey.split(";")
                x = int(cords[0])
                y = int(cords[1]) 
                blocks.append(Block(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE))

while running:
    # draw bgs
    screen.fill((0, 0, 0))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_s] and keys[pygame.K_LCTRL]:
                with open("levels/map.json", 'w') as file:
                    json.dump([f"{block.rect.x//TILE_SIZE};{block.rect.y//TILE_SIZE}" for block in blocks], file)
                  
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: # left click
                pos = pygame.mouse.get_pos()
                grid_pos = (pos[0] // (SCALE * TILE_SIZE), pos[1] // (SCALE * TILE_SIZE)) # from mouse click to grid position
                real_pos = (grid_pos[0] * TILE_SIZE, grid_pos[1] * TILE_SIZE)  # from grid position to ui position
                for block in blocks.copy():
                    if block.rect.collidepoint(real_pos):
                        blocks.remove(block)
                        break
                else:
                    blocks.append(Block(real_pos[0], real_pos[1], TILE_SIZE))

    # Debugging
    # for block in blocks: # updating enemies
    #     block.update(0.1)

    [pygame.draw.rect(screen, (0, 255, 0), block.rect, 1) for block in blocks] # draw block rects 

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
