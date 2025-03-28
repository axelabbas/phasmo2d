from math import sqrt
import pygame

class Player:
    def __init__(self, x, y):
        self.speed = 200
        self.player_size = 16
        self.x = x
        self.y = y
        self.playerRect = pygame.Rect(self.x, self.y, self.player_size, self.player_size)
    
    def update(self, screen, moving, dt, blocks: list[pygame.Rect]):
        dx = moving["right"] - moving["left"]
        dy = moving["down"] - moving["up"]
        
        # Normalize diagonal movement
        magnitude = sqrt(dx * dx + dy * dy)
        if magnitude > 0:
            dx /= magnitude
            dy /= magnitude
        
        movement_x = self.speed * dx * dt
        movement_y = self.speed * dy * dt
        temp_rect = self.playerRect.copy()
        
        # X movement
        temp_rect.x = self.x + movement_x
        collision_idx = temp_rect.collidelist(blocks)
        if collision_idx == -1:
            self.x += movement_x
        else:
            # Adjust position based on collision normal
            block = blocks[collision_idx]
            if movement_x > 0:
                self.x = block.left - self.player_size
            else:
                self.x = block.right
        
        # Y movement
        temp_rect.x = self.x  # Update X position
        temp_rect.y = self.y + movement_y
        collision_idx = temp_rect.collidelist(blocks)
        if collision_idx == -1:
            self.y += movement_y
        else:
            block = blocks[collision_idx]
            if movement_y > 0:
                self.y = block.top - self.player_size
            else:
                self.y = block.bottom
        
        # Update final rect
        self.playerRect.x = self.x
        self.playerRect.y = self.y
        self.draw(screen)
    
    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.playerRect)