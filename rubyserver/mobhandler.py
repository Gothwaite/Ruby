import base64, json
from server import *
import pygame, random

class MobHandler:

    def __init__(self):
        self.mob_list = []
        self.clock = pygame.time.Clock()
        
    def mob_spawn(self, factory):

        if len(self.mob_list) == 0:
            new_mob = Goblin(200, 300, 2, 60, 10) #x, y, zone, mhp, damage. placeholder
            new_mob2 = Goblin(250, 350, 2, 30, 5)
            new_mob3 = Goblin(300, 450, 2, 100, 15)
            self.mob_list.append(new_mob)
            self.mob_list.append(new_mob2)
            self.mob_list.append(new_mob3)

    def handler(self, factory):

        self.mob_spawn(factory)
        self.wander()
        self.aggro(factory)
        self.target_finder(factory)
        self.move_towards_target(factory)
        self.attack_target(factory)
        self.send_mob_updates(factory)

    def aggro(self, factory):
        for mob in self.mob_list:
            for i in range(0, len(factory.clients)):
                if abs(mob.x - factory.clients[i].x) < mob.aggro_range and abs(mob.y - factory.clients[i].y) < mob.aggro_range:
                    if i not in mob.enemies:
                        mob.enemies.append(i)

    def wander(self):
        for mob in self.mob_list:
            if mob.target == None:
                mob.wandering = True
            else:
                mob.wandering = False
            if mob.wandering == True and mob.wander == [0, 0]:
                direction = random.randint(1,4)
                distance = random.randint(25,100)
                mob.wander = [direction, distance]
            if mob.wander != [0, 0] and mob.wandering == True:
                if mob.wander[0] == 1: #right
                    mob.dir = 'right'
                    mob.xm = 1
                    mob.ym = 0
                elif mob.wander[0] == 2: #left
                    mob.dir = 'left'
                    mob.xm = -1
                    mob.ym = 0
                elif mob.wander[0] == 3: #down
                    mob.dir = 'down'
                    mob.ym = 1
                    mob.xm = 0
                elif mob.wander[0] == 4: #up
                    mob.dir = 'up'
                    mob.ym = -1
                    mob.xm = 0
                mob.wander[1] -= 1
                if mob.wander[1] <= 0:
                    self.find_spawn(mob)
                    
    def find_spawn(self, mob):
        diff_x = abs(mob.x - mob.initial_x)
        diff_y = abs(mob.y - mob.initial_y)
        direction = random.randint(1,2)
        if direction == 1:
            mob.wander[1] = diff_x + random.randint(25,100)
            if mob.x - mob.initial_x > 0:
                mob.wander[0] = 2
            else:
                mob.wander[0] = 1
        else:
            mob.wander[1] = diff_y + random.randint(25,100)
            if mob.y - mob.initial_y > 0:
                mob.wander[0] = 4
            else:
                mob.wander[0] = 3
             
        
        
    def attack_target(self, factory):
        tick = self.clock.tick()
        for mob in self.mob_list:
            mob.attack_timer += tick

            if mob.attack_timer > mob.attack_speed:

                if mob.target != None:
                    if abs(factory.clients[mob.target].x - mob.x) < 45:
                        if abs(factory.clients[mob.target].y - mob.y) < 45:
                            print 'attacked player %d' % (mob.target)
                            index = mob.target
                            packet = json.dumps([{"packet": ServerPackets.SMobAttacked, "damage": mob.damage, "player_id": index}])
                            factory.proto.sendDataTo(mob.target, packet)
                            mob.attack_timer = 0
 
            
    def move_towards_target(self, factory):
        for mob in self.mob_list:
            if mob.target != None:

                if abs((factory.clients[mob.target].x) - mob.x) < 30:
                    mob.xm = 0
                if factory.clients[mob.target].x - 20 > mob.x:
                    mob.xm += 1
                else:
                    mob.xm -= 1
                if abs(factory.clients[mob.target].y - mob.y) < 30:
                    mob.ym = 0
                if factory.clients[mob.target].y -20 > mob.y:
                    mob.ym += 1
                else:
                    mob.ym -= 1
            elif mob.wandering == False: #if no target, stand still
                mob.xm = 0
                mob.ym = 0
            if mob.xm > 6: #speed cap is 6
                mob.xm -= 2
            if mob.ym > 6:
                mob.ym -= 2
            if mob.xm < -6:
                mob.xm += 2
            if mob.ym < -6:
                mob.ym += 2
            mob.x += mob.xm
            mob.y += mob.ym
 

    def target_finder(self, factory):
        for mob in self.mob_list:
            if mob.enemies != []:
                n = 5000
                try:
                    for enemy in mob.enemies:
                         if n > abs(factory.clients[enemy].x - mob.x) + abs(factory.clients[enemy].y - mob.y) and mob.zone == factory.clients[enemy].zone:
                             n = abs(factory.clients[enemy].x - mob.x) + abs(factory.clients[enemy].y - mob.y)
                             closest_enemy = enemy
                    try:         
                        mob.target = closest_enemy
                    except UnboundLocalError: #no target
                        mob.target = None
                        mob.enemies = []
                        mob.dir = 'standing'

                except IndexError: #the aggressor logged out,
                    mob.enemies = []
                    mob.target = None
                    mob.dir = 'standing'

                         
    def send_mob_updates(self, factory):
        for i in range(0, len(factory.clients)):
            for mob in self.mob_list:
                if mob.zone == factory.clients[i].zone:
                    if mob.chp <= 0:
                        gold = self.loot_handler(factory, mob.mhp)
                        packet = json.dumps([{"packet": ServerPackets.SMobDied, "name": mob.name, "gold":gold}])
                    else:
                        try:
                            if abs(mob.x - factory.clients[mob.target].x) > abs(mob.y - factory.clients[mob.target].y):
                                if mob.x - factory.clients[mob.target].x < 0:
                                    mob.dir = 'right'
                                else:
                                    mob.dir = 'left'
                            else:
                                if mob.y - factory.clients[mob.target].y < 0:
                                    mob.dir = 'down'
                                else:
                                    mob.dir = 'up'
                        except TypeError:
                            pass
                        packet = json.dumps([{"packet": ServerPackets.SMobUpdate, "name": mob.name, "x":mob.x, "y":mob.y, "zone":mob.zone, "chp":mob.chp, "mhp":mob.mhp, "direction":mob.dir}])
                    factory.proto.sendDataTo(i, packet)
        for mob in self.mob_list:
            if mob.chp <= 0:
                self.mob_list.remove(mob)

    def loot_handler(self, factory, mhp):
        return mhp * 2
        
