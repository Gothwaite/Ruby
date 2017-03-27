import player, controller, pygame, math
import globalvars as g
from __builtin__ import True

class Model:
    
    def __init__(self):
        
        self.my_player = player.Player(0, 500, 300) #makes my_player so the client doesn't panic, is replaced with server's initialize immediately
        self.id = 0
        self.controller = controller.Controller()
        self.line = 'empty'
        self.players_list = []
        self.mob_list = []
        self.static_list = {}
        self.clock = pygame.time.Clock()
        self.attack_timer = 0
        self.attack_speed = 700
        self.update_count = 0
        self.static_list = []
        self.at_shop = False


        
    def new_line(self, line):
        self.line = line

    def check_death(self):
        if self.my_player.chp <= 0:
            old_zone = self.my_player.zone
            self.my_player.chp = self.my_player.mhp
            self.my_player.zone = 1
            self.my_player.x = 500
            self.my_player.y = 300
            self.players_list = [self.my_player]
            self.mob_list = []
            g.tcpConn.sendZoneUpdate(self.my_player.zone, old_zone)  # @UndefinedVariable

    def my_player_data(self):
        for players in self.players_list:
            if players.id == self.id:
                self.my_player = players
        
    def attack_handler(self):
        tick = self.clock.tick()
        self.attack_timer += tick
        if self.controller.check_for_attack() and self.attack_timer >= self.attack_speed:
            if self.at_shop == True:
                self.purchase(self.controller.check_ui_click())
                self.attack_timer = 0
                return False, 0

            self.attack_timer = 0
            swing_angle = self.weapon_collision_handler()
            return True, swing_angle
        return False, 0
            
    def weapon_collision_handler(self):
        mouse_pos = pygame.mouse.get_pos()
        swing_from = (400, 300)
        swing_angle = math.degrees(math.atan2((swing_from[1]-mouse_pos[1]), float(mouse_pos[0]-swing_from[0]))) #angle of attack
        if swing_angle < 0:
            swing_angle += 360
        swing_range = [swing_angle + 75, swing_angle - 75]
        for mob in self.mob_list: #check if sword hits a mob
            if abs(int(mob.x) - int(self.my_player.x)) < 95 and abs(int(mob.y) - int(self.my_player.y)) < 95:
                mob_angle = math.degrees(math.atan2((self.my_player.y - int(mob.y)), -float(self.my_player.x - int(mob.x))))
                if mob_angle < 0:
                    mob_angle += 360
                if mob_angle >= swing_range[1] and mob_angle <= swing_range[0] or mob_angle - 360 >= swing_range[1] and mob_angle - 360 <= swing_range[0] or mob_angle + 360 >= swing_range[1] and mob_angle + 360 <= swing_range[0]:
                    g.tcpConn.sendMobHit(mob.name, self.my_player.damage)  # @UndefinedVariable
        print swing_angle
        return swing_angle
        
    
    def update_my_coordinates(self): #update coordinates and let view know

        x, y = self.controller.check_movement()
        if x != 0 or y != 0:
            self.my_player.moving = True
        else:
            self.my_player.moving = False
        self.my_player.x += x * self.my_player.speed
        self.my_player.y += y * self.my_player.speed
        if self.update_count > 5:
            mouse_pos = pygame.mouse.get_pos()
            swing_angle = math.degrees(math.atan2((300-mouse_pos[1]), float(mouse_pos[0]-400))) #angle of attack
            if swing_angle < 0:
                swing_angle += 360
            self.update_count = 0
            self.my_player.angle = swing_angle
            
        else:
            self.update_count += 1
    def check_zone_change(self): #if player leaves boundary and there is another map on that side, change zones
        old_zone = self.my_player.zone
        new_zone = 0
        if self.my_player.y < 15:
            new_zone = -4
        if self.my_player.y > 955:
            new_zone = 4
        if self.my_player.x < 15:
            if self.my_player.zone not in (1,5,9):
                new_zone = -1
        if self.my_player.x > 955:
            if self.my_player.zone not in (4,8,12):
                new_zone = 1
        if new_zone + self.my_player.zone <= 12 and self.my_player.zone + new_zone >= 1 and new_zone != 0:
            self.my_player.zone += new_zone
            if new_zone == 4:
                self.my_player.y = 20
            if new_zone == -4:
                self.my_player.y = 950                        
            if new_zone == 1:
                self.my_player.x = 20  
            if new_zone == -1:
                self.my_player.x = 950  
            g.tcpConn.sendZoneUpdate(self.my_player.zone, old_zone)  # @UndefinedVariable
            self.players_list = [self.my_player] 
            self.mob_list = []
            return True 
                
    def update_camera(self):
        return self.my_player.x, self.my_player.y
    
    def update_to_server(self): #send position to server
        try:
            g.tcpConn.sendPlayerPos(self.my_player.x, self.my_player.y, self.my_player.zone, self.my_player.chp, self.my_player.mhp, self.my_player.angle, self.my_player.moving)  # @UndefinedVariable

        except:
            print "error sending"
    
    def players_and_mobs_update(self, data): #add players and mobs to dictionary
        data_dict = {player[0]:player[1:3] for player in data}
        self.players_and_mobs_list = data_dict
        
    def static_update(self, data):
        datas = {static[0]:static[1:3] for static in data}
        self.static_list = datas

    def check_static_collision(self):
        for static in self.static_list:
            if static.zone == self.my_player.zone:
                if abs(self.my_player.x - static.x) < 90:
                    if abs(self.my_player.y - static.y) < 90:
                        #collision
                        if static.name == 'shop': #bring up shop menu
                            self.at_shop = True
                    else:
                        self.at_shop = False        
                else:
                    self.at_shop = False
                    
    def purchase(self, upgrade):
        if upgrade == 'damage':
            purchase = self.my_player.upgrade_levels[0]
        elif upgrade == 'attack_speed':
            purchase = self.my_player.upgrade_levels[1]
        elif upgrade == 'armor':
            purchase = self.my_player.upgrade_levels[2]
        elif upgrade == 'max_health':
            purchase = self.my_player.upgrade_levels[3]
        else:
            return
        if self.my_player.gold >= purchase * 100 + 100:
            self.my_player.gold -= purchase * 100 + 100
            if upgrade == 'damage':
                self.my_player.damage += 2
                self.my_player.upgrade_levels[0] += 1
            elif upgrade == 'attack_speed':
                self.attack_speed = self.attack_speed * .9
                self.my_player.upgrade_levels[1] += 1
            elif upgrade == 'armor':
                self.my_player.upgrade_levels[2] += 1
                #to be added
            elif upgrade == 'max_health':
                self.my_player.mhp += 25
                self.my_player.upgrade_levels[3] += 1

