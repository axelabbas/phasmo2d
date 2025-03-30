import json
import pygame
from models.player import Player
from models.block import Block
from light import LightSystem  # Our new class

# Initialize pygame
pygame.init()

# Constants
HEIGHT, WIDTH = 640, 360
TILE_SIZE = 16
FPS = 60

# Pygame setup
window = pygame.display.set_mode((HEIGHT, WIDTH))
clock = pygame.time.Clock()

# Player setup
player = Player(WIDTH // 2 - 16 // 2, HEIGHT // 2 - 16 // 2)

# Movement tracking
moving = {"left": False, "right": False, "up": False, "down": False}

# Load level from JSON
blocks = []
with open("levels/map.json", 'r') as file:
    level = json.load(file)
    for item in level:
        x, y = map(int, item.split(";"))
        cell = Block(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE)
        blocks.append(cell.rect)  # We just need the rects for FOV

# Initialize FOV system
fov_system = LightSystem(
    blocks=blocks,
    fov_angle=90,
    base_ray_count=90,
    view_distance=200,
    ray_density=0.5,
    grid_size=64
)

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

    # Clear screen
    window.fill((0, 0, 0))
   
    mouse_pos = pygame.mouse.get_pos()
    player_pos = (player.x + player.player_size//2, player.y + player.player_size//2)


    LIGHT_COLOR = (255, 255, 255)  # White light
    LIGHT_ALPHA = 80  # Semi-transparent

    # In your main game loop (replace the darkness rendering):
    # Calculate FOV
    rays = fov_system.calculate_rays(player_pos, mouse_pos=mouse_pos)

    # Draw blocks (walls) - do this before lighting effects
    for block in blocks:
        pygame.draw.rect(window, (255, 0, 255), block)

    # Draw combined lighting effect
    lighting = fov_system.create_combined_lighting(
        (HEIGHT, WIDTH), 
        rays, 
        player_pos,
        light_color=LIGHT_COLOR,
        light_alpha=LIGHT_ALPHA
    )
    window.blit(lighting, (0, 0))

    # Draw blocks (walls)
    player.update(window, moving=moving, dt=dt, blocks=blocks)
    # For debugging: draw rays (set to True to visualize)
    if False:
        for start, end in rays:
            pygame.draw.line(window, (255, 255, 0, 50), start, end, 1)
    
    # Update display
    pygame.display.flip()
    
    # Frame rate control
    dt = max(0.001, min(0.1, clock.tick(FPS) / 1000))

pygame.quit()