import pygame


class AssetsSystem:
    _loaded_sprites = {}

    @staticmethod
    def load_sprite_from_spriteimg(path, scale, isAlpha): # not tested
        if path in AssetsSystem._loaded_sprites:
            return AssetsSystem._loaded_sprites[path]
        if isAlpha:
            sprite = pygame.image.load(path).convert_alpha()
        else:
            sprite = pygame.image.load(path).convert()
        sprite = pygame.transform.scale(sprite, (int(sprite.get_width() * scale), int(sprite.get_height() * scale)))
        AssetsSystem._loaded_sprites[path] = sprite
        return sprite
    
    @staticmethod
    def load_sprite_from_spritesheet(cords,path, width, height, rows, cols, scale, isAlpha):
        sprite =AssetsSystem.load_spritesheet(path, width, height, rows, cols, scale, isAlpha)[cords[0]][cords[1]]
        return sprite
    @staticmethod
    def load_spritesheet(path, width, height, rows, cols, scale, isAlpha):
        if path in AssetsSystem._loaded_sprites:
            return AssetsSystem._loaded_sprites[path]
        if isAlpha:
            sheet = pygame.image.load(path).convert_alpha()
        else:
            sheet = pygame.image.load(path).convert()

        sprites = []
        for row in range(rows):
            colSprites = []
            for col in range(cols): 
                sprite = sheet.subsurface((col * width, row * height, width, height))
                
                sprite = pygame.transform.scale(sprite, (int(width * scale), int(height * scale)))
               
                colSprites.append(sprite)
            sprites.append(colSprites)
        AssetsSystem._loaded_sprites[path] = sprites
        return sprites