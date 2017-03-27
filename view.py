
import pygame, os, model, csv, static


class View(object):

    def __init__(self):
        pygame.init()
        self.model = model.Model()
        self.slash_img = pygame.image.load(os.path.join("slash.png"))
        self.display = pygame.display.set_mode((800, 600))
        self.screen = pygame.Surface((1000,1000))
        self.bif = pygame.image.load("grass.png") 
        self.slash_img = pygame.image.load("slash.png")
        self.shop_ui = pygame.image.load("data\shop_ui.png")
        self.did_swing = False
        self.swing_angle = 0
        self.load_static()

        
    def tick(self): #pseudo main loop
        self.model.check_death()
        self.model.check_zone_change()
        self.model.update_my_coordinates()
        self.model.check_static_collision()
        self.did_swing, self.swing_angle = self.model.attack_handler()
        self.camera_x, self.camera_y =  self.model.update_camera()
        self.model.update_to_server()
        self.model.my_player_data()
        self.draw_updates()
        
    def draw_updates(self): #draw everything
        self.screen.blit(self.bif,(0,0))
        self.draw_static()
        self.draw_swing()
        self.draw_players()
        self.draw_mobs()
        self.display.fill((0,0,0)) #screen is the world, display is what part of it the player can see
        self.display.blit(self.screen,(0 - self.camera_x + 400, 0 - self.camera_y + 300))
        self.draw_ui()
        pygame.display.flip()
    
    def rot_center(self, image, angle): #rotate image around center. not my code
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image
    
    def draw_mobs(self):
        for mob in self.model.mob_list: #draw mobs
            frame = 44
            if mob.frame_delay == 0:
                if mob.dir == 'down':
                    if mob.pframe < 5:
                        frame = mob.pframe + 1
                    else:
                        frame = 0
                if mob.dir == 'right':
                    if mob.pframe < 16 and mob.pframe > 10:
                        frame = mob.pframe + 1
                    else:
                        frame = 11     
                if mob.dir == 'up':
                    if mob.pframe < 28 and mob.pframe > 21:
                        frame = mob.pframe + 1
                    else:
                        frame = 22
                if mob.dir == 'left':
                    if mob.pframe < 39 and mob.pframe > 32:
                        frame = mob.pframe + 1
                    else:
                        frame = 33  
 
                mob.frame_delay = 2
                
            else:
                mob.frame_delay -= 1       
                frame = mob.pframe
            self.screen.blit(mob.ani[frame], (int(mob.x - 5), int(mob.y - 5)))
            mob.pframe = frame
            pygame.draw.rect(self.screen, (255, 0, 0), (int(mob.x) + 7, int(mob.y) - 7, 30, 5)) #draw health bar (next line too)
            pygame.draw.rect(self.screen, (0, 255, 0), (int(mob.x) + 7, int(mob.y) - 7, (mob.chp / float(mob.mhp)) * 30, 5))
            self.screen.blit(pygame.font.SysFont('mono', 11, bold=True).render(mob.name, True, (255, 0, 0)), ((int(mob.x) + 2), (int(mob.y) - 19)))  
            
    def draw_players(self):
        for player in self.model.players_list: #draw players   
            frame = 0
            if player.frame_delay == 0: #down
                if 225 < player.angle < 315:
                    if player.pframe < 5:
                        frame = player.pframe + 1
                    else:
                        frame = 1
                    if player.moving == False:
                        frame = 0
                
                if player.angle <= 45 or player.angle >= 315: #right
                    if player.pframe < 16 and player.pframe > 12:
                        frame = player.pframe + 1
                    else:
                        frame = 13   
                    if player.moving == False:
                        frame = 12  
                if 135 > player.angle > 45:
                    if player.pframe < 10 and player.pframe > 6:#up
                        frame = player.pframe + 1
                    else:
                        frame = 7
                    if player.moving == False:
                        frame = 6
                if 225 >=player.angle >= 135:
                    if player.pframe < 22 and player.pframe > 18: #left
                        frame = player.pframe + 1
                    else:
                        frame = 19  
                    if player.moving == False:
                        frame = 18
 
                player.frame_delay = 2
                
            else:
                player.frame_delay -= 1       
                frame = player.pframe

            self.screen.blit(player.ani[frame], (int(player.x - 16), int(player.y - 4)))
            player.pframe = frame
            
            pygame.draw.rect(self.screen, (255, 0, 0), (int(player.x), int(player.y - 10), 30, 5))
            pygame.draw.rect(self.screen, (0, 255, 0), (int(player.x), int(player.y - 10), (player.chp / float(player.mhp)) * 30, 5))
            self.screen.blit(pygame.font.SysFont('mono', 11, bold=True).render("%d" % player.id, True, (255, 255, 255)), ((int(player.x) - 5), (int(player.y) - 21))) 
            
    def draw_static(self):
        for static in self.model.static_list:
            if static.zone == self.model.my_player.zone:
                self.screen.blit(static.image, (static.x - static.radius, static.y - static.radius))

            
    def draw_swing(self):
        if self.did_swing == True: #draw swing animation
            slash = self.rot_center(self.slash_img, self.swing_angle)
            self.screen.blit(slash, (self.model.my_player.x - 43, self.model.my_player.y - 43))
            
    def draw_ui(self):
        self.display.blit(pygame.font.SysFont('mono', 14, bold=True).render("Zone: " + str(self.model.my_player.zone), True, (255, 255, 255)), (0,0))
        self.display.blit(pygame.font.SysFont('mono', 14, bold=True).render("Gold: " + str(self.model.my_player.gold), True, (255, 255, 255)), (0,16))
        if self.model.at_shop == True:
            self.display.blit(self.shop_ui, (200, 150))
            self.display.blit(pygame.font.SysFont('mono', 16, bold=True).render(str(self.model.my_player.upgrade_levels[0]), True, (0, 0, 0)), (370,275))
            self.display.blit(pygame.font.SysFont('mono', 16, bold=True).render(str(self.model.my_player.upgrade_levels[1]), True, (0, 0, 0)), (370,315))
            self.display.blit(pygame.font.SysFont('mono', 16, bold=True).render(str(self.model.my_player.upgrade_levels[2]), True, (0, 0, 0)), (370,355))
            self.display.blit(pygame.font.SysFont('mono', 16, bold=True).render(str(self.model.my_player.upgrade_levels[3]), True, (0, 0, 0)), (370,395))
            self.display.blit(pygame.font.SysFont('mono', 16, bold=True).render(str(self.model.my_player.upgrade_levels[0] * 100 + 100), True, (0, 0, 0)), (450,275))
            self.display.blit(pygame.font.SysFont('mono', 16, bold=True).render(str(self.model.my_player.upgrade_levels[1] * 100 + 100), True, (0, 0, 0)), (450,315))
            self.display.blit(pygame.font.SysFont('mono', 16, bold=True).render(str(self.model.my_player.upgrade_levels[2] * 100 + 100), True, (0, 0, 0)), (450,355))
            self.display.blit(pygame.font.SysFont('mono', 16, bold=True).render(str(self.model.my_player.upgrade_levels[3] * 100 + 100), True, (0, 0, 0)), (450,395))
    def load_static(self):
        pathWork = os.getcwd()
        pathData = os.path.join(pathWork, os.path.join("data", "static.csv"))
        with open(pathData, 'rb') as file:
            reader = csv.reader(file)
            temp_static_list = list(reader) 
            
        for item in temp_static_list:
            new_static = static.Static(item[0], int(item[1]), int(item[2]), int(item[3]), int(item[4]), item[5])
            self.model.static_list.append(new_static)
            
            
            
        
