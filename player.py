from math import sqrt
import pygame


class Player:
    def __init__(self, x, y):
        self.speed = 500
        self.player_size = 16
        self.playerRect = pygame.Rect(x, y, self.player_size, self.player_size)
    
    def update(self,screen, moving, dt):
        dx = moving["right"] - moving["left"]
        dy = moving["down"] - moving["up"]
        magnitude = sqrt(dx * dx + dy * dy)

        if magnitude > 0:  # Avoid division by zero
            dx /= magnitude
            dy /= magnitude

        # Update player position
        self.playerRect.x += self.speed * dx * dt
        self.playerRect.y += self.speed * dy * dt
        self.draw(screen)
    def draw(self,screen):
        pygame.draw.rect(screen, (255, 255, 255), self.playerRect)


        