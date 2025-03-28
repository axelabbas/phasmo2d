import json
import pygame
from models.player import Player
from models.block import Block
from shadows import FOVSystem

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
fov_system = FOVSystem(
    blocks=blocks,
    fov_angle=50,
    base_ray_count=20,
    view_distance=200,
    ray_density=.4,
    grid_size=16
)

running = True
dt = 0.1
darkness_surface = pygame.Surface((HEIGHT, WIDTH), pygame.SRCALPHA)
light_surface = pygame.Surface((HEIGHT, WIDTH), pygame.SRCALPHA)

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

    # Draw blocks only in visible area
    view_rect = pygame.Rect(player.x - 300, player.y - 200, 600, 400)
    for block in blocks:
        if view_rect.colliderect(block):
            pygame.draw.rect(window, (255, 255, 255), block)
    
    # Calculate FOV with optimized ray count
    visible_blocks = fov_system._get_blocks_in_area(player.x, player.y, fov_system.view_distance)
    rays = fov_system.calculate_fov(player_pos, mouse_pos=mouse_pos)
    
    pygame.draw.rect(window, (255,0,0), pygame.Rect(3*TILE_SIZE, 3* TILE_SIZE, TILE_SIZE, TILE_SIZE))
    # Optimized lighting
    lighting = fov_system.create_combined_lighting((HEIGHT, WIDTH), rays, player_pos)
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