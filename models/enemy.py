import pygame

class Enemy:
    def __init__(self, x, y, tile_size):
        self.tile_size = tile_size
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, tile_size, tile_size)

    def update(self, playerPos: tuple[int,int]):
        toVector = pygame.math.Vector2.normalize(pygame.math.Vector2((playerPos[0] - self.x, playerPos[1] - self.y)))
        self.x += toVector.x
        self.rect.x = self.x

        self.y += toVector.y
        self.rect.y = self.y

