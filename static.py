import pygame

class Static:
    
    def __init__(self, name, x, y, zone, radius, image):
        
        self.name = name
        self.y = y
        self.x = x
        self.zone = zone
        self.radius = radius
        self.image = pygame.image.load(image)