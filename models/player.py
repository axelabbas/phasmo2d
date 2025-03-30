from math import sqrt
import math
import pygame

from fov_systems import RadialFOVSystem

class Player:
    def __init__(self, x, y, fov_system: RadialFOVSystem,):
        self.speed = 200
        self.player_size = 16
        self.x = x
        self.y = y
        self.playerRect = pygame.Rect(self.x, self.y, self.player_size, self.player_size)
        self.fov_system = fov_system
        self.lookingPoint = (0,0)
        self.facing_angle = math.atan2(self.lookingPoint[1] - self.y, self.lookingPoint[0] - self.x) 
    
    def update(self, screen, moving, dt, blocks: list[pygame.Rect], lookingPoint: tuple[int,int]):

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

        self.lookingPoint = lookingPoint
        self.facing_angle = math.atan2(self.lookingPoint[1] - self.y, self.lookingPoint[0] - self.x)

        self.draw(screen)
    
    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.playerRect)
    
    def is_target_visible(self,target):
        return self.fov_system.is_visible((self.x + (self.player_size//2), self.y + (self.player_size // 2)), target, self.facing_angle)
    def getFOVPolygon(self, size: tuple[int,int]):
        return self.fov_system.draw_fov_polygon(size,(self.x + (self.player_size//2), self.y + (self.player_size // 2)), self.facing_angle)
