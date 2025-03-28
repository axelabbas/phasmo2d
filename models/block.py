import pygame


class Block:
    def __init__(self, x, y, tile_size):
        self.tile_size = tile_size
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, tile_size, tile_size)

    def update():
        pass

