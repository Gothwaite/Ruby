import pygame
from twisted.internet import reactor
from os import sys
import globalvars as g

class Controller:
    
    def check_movement(self):
        x = 0
        y = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                reactor.stop()  # @UndefinedVariable
                pygame.quit()
                sys.exit()
      
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_q]:
            g.tcpConn.sendZoneUpdate(1, 1)  # @UndefinedVariable

        if pressed[pygame.K_w]:
            y -= 1
        if pressed[pygame.K_s]:
            y += 1
        if pressed[pygame.K_a]:
            x -= 1
        if pressed[pygame.K_d]:
            x += 1
        return x, y
                
    def check_for_attack(self):
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]:
            return True
        
    def check_ui_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if 520 < mouse_pos[0] < 580:
            if 270 < mouse_pos[1] < 300:
                return 'damage'
            if 310 < mouse_pos[1] < 340:
                return 'attack_speed'
            if 350 < mouse_pos[1] < 380:
                return 'armor'
            if 390 < mouse_pos[1] < 420:
                return 'max_health'
        return 'none'
            
        
        
        
        
        
        
        
        
        
        
        