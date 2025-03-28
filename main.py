import json
import pygame
from math import sqrt
from player import Player
from shadows import Shadow

# Initialize pygame
pygame.init()

# Constants
HEIGHT, WIDTH = 1000,1000
TILE_SIZE = 16

# Pygame setup
window = pygame.display.set_mode((HEIGHT, WIDTH))
clock = pygame.time.Clock()

# Player setup
player = Player(WIDTH // 2 - 16 // 2, HEIGHT // 2 - 16 // 2)

# Movement tracking
moving = {"left": False, "right": False, "up": False, "down": False}

# Shadow system
shadow = Shadow()
blocks = []

# Load level from JSON
with open("levels/map.json", 'r') as file:
    level = json.load(file)  # No need for `loads` since we read from file
    max_x, max_y = shadow.loadMap(level)
    for item in level:
        x, y = map(int, item.split(";"))
        blocks.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    
# Generate edges
shadow.convert_tilemap_to_polymap(0,0, max_x, max_y, 16)
# Main game loop
running = True
dt = 0.1
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key in [pygame.K_LEFT, pygame.K_a]:
                moving["left"] = True
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                moving["right"] = True
            elif event.key in [pygame.K_UP, pygame.K_w]:
                moving["up"] = True
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                moving["down"] = True
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                moving["left"] = False
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                moving["right"] = False
            elif event.key in [pygame.K_UP, pygame.K_w]:
                moving["up"] = False
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                moving["down"] = False

    # Player movement calculations
    # update with moves
    player.update(window, moving=moving, dt=dt)

    # Render
    window.fill((0, 0, 0))  # Clear screen

    # Draw blocks (walls)
    for block in blocks:
        pygame.draw.rect(window, (255, 0, 255), block)

    # Draw shadows (edges)
    # for edge in edges:
    #     pygame.draw.line(window, (255, 255, 255), (edge.sx, edge.sy), (edge.ex, edge.ey), 1)
    #     pygame.draw.circle(window, (255, 0, 0), (edge.sx, edge.sy), 1)
    #     pygame.draw.circle(window, (255, 0, 0), (edge.ex, edge.ey), 1)
  
    for edge in shadow.edges:
        pygame.draw.line(window, (255, 255, 255), (edge.sx, edge.sy), (edge.ex, edge.ey), 1)
        pygame.draw.circle(window, (255, 0, 0), (edge.sx, edge.sy), 1)
        pygame.draw.circle(window, (255, 0, 0), (edge.ex, edge.ey), 1)
  


    # Update display
    pygame.display.flip()

    # Frame rate control
    dt = max(0.001, min(0.1, clock.tick(60) / 1000))

pygame.quit()
