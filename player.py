import SpriteSheet, pygame

class Player:
    
    def __init__(self, i, x, y):
        
        self.id = i
        self.x = x
        self.y = y
        self.speed = 10
        self.zone = 1
        self.color = (0, 255, 0)
        self.damage = 10
        self.gold = 0
        self.chp = 100
        self.mhp = 100
        self.angle = 0
        self.moving = False
        self.img = SpriteSheet.spritesheet("data/knight.png")
        self.pframe = 0
        self.frame_delay = 2
        self.upgrade_levels = [0,0,0,0]
        frames = []
        for n in range(0,4): #this code handles spritesheets, turning them into a list of images that can be cycled through to create animations
            top = 64*n
            for i in range(0,6):
                left = 64*i
                width = 64
                height = 64
                frames.append(pygame.Rect(left, top, width, height))
        self.ani = self.img.images_at(frames, (0,0,0))    