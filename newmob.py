import SpriteSheet, pygame

class NewMob:
    
    def __init__(self, name, x, y, chp, mhp, direction):
        self.name = name
        self.x = x
        self.y = y
        self.chp = chp
        self.mhp = mhp
        self.dir = direction
        if self.mhp == 30:
            self.img = SpriteSheet.spritesheet("data/goblin.png")
        elif self.mhp == 60:
            self.img = SpriteSheet.spritesheet("data/red_goblin.png")
        elif self.mhp == 100:
            self.img = SpriteSheet.spritesheet("data/blue_goblin.png")
        self.pframe = 0
        self.frame_delay = 2
        frames = []
        for n in range(0,5): #this code handles spritesheets, turning them into a list of images that can be cycled through to create animations
            top = 64*n
            for i in range(0,11):
                left = 64*i
                width = 64
                height = 64
                frames.append(pygame.Rect(left, top, width, height))
        self.ani = self.img.images_at(frames, (0,0,0))    