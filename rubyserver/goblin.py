

class Goblin:
    mob_id = 0

    def __init__(self, x, y, zone, hp, dmg):
        self.name = 'Goblin' + str(Goblin.mob_id)
        self.xm = 0
        self.ym = 0
        self.x = x
        self.y = y
        self.initial_x = x
        self.initial_y = y
        self.chp = hp
        self.mhp = hp
        self.wandering = True
        self.wander = [0, 0]
        self.zone = zone
        Goblin.mob_id += 1
        self.enemies = []
        self.target = None
        self.attack_speed = 300
        self.attack_timer = 0
        self.value = 10
        self.damage = dmg
        self.aggro_range = 100
        self.dir = 'standing'

