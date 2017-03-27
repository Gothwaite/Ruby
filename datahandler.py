import json
import globalvars as g
import newmob
import player

class ServerPackets:
    SPlayerCoords,   \
    SCleanPlayersList,   \
    SMobUpdate, \
    SMobDied,   \
    SMobAttacked, \
    SInitPlayer,  \
    SHealthUpdate \
    = range(7)
    
class ClientPackets:
    CMoved, \
    CZone,   \
    CMobHit,   \
    CHealthUpdate \
    = range(4)
    
class DataHandler():
    def handleData(self, data):
        jsonData = json.loads(data)
        packetType = jsonData[0]["packet"]
        
        if packetType == ServerPackets.SPlayerCoords:
            self.handlePlayerCoords(jsonData)
        elif packetType == ServerPackets.SCleanPlayersList:
            self.clean_players_list(jsonData)
        elif packetType == ServerPackets.SMobUpdate:
            self.mob_update(jsonData)
        elif packetType == ServerPackets.SMobDied:
            self.mob_died(jsonData)
        elif packetType == ServerPackets.SMobAttacked:
            self.mob_attacked(jsonData)
        elif packetType == ServerPackets.SHealthUpdate:
            self.handlePlayerHP(jsonData)
        elif packetType == ServerPackets.SInitPlayer:
            self.init_player(jsonData)

    def handlePlayerCoords(self, jsonData):
        if jsonData[0]["zone"] == g.view.model.my_player.zone:   # @UndefinedVariable
            for players in g.view.model.players_list:  # @UndefinedVariable
                if players.id == jsonData[0]['player_id']:
                    players.x = jsonData[0]['x']
                    players.y = jsonData[0]['y'] 
                    players.angle = jsonData[0]['angle'] 
                    players.moving = jsonData[0]['moving'] 
                    return
            print "new"
            new_player = player.Player(jsonData[0]['player_id'], jsonData[0]['x'], jsonData[0]['y']) 
            new_player.zone = g.view.model.my_player.zone  # @UndefinedVariable
            g.tcpConn.sendHealthUpdate(g.view.model.my_player.chp, g.view.model.my_player.mhp)  # @UndefinedVariable
            g.view.model.players_list.append(new_player)  # @UndefinedVariable
            
    def handlePlayerHP(self, jsonData):
        for players in g.view.model.players_list:  # @UndefinedVariable
            if players.id == jsonData[0]['player_id']:
                players.chp = jsonData[0]['chp'] 
                players.mhp = jsonData[0]['mhp'] 
                return
        new_player = player.Player(jsonData[0]['player_id'], -100, -100) 
        new_player.zone = g.view.model.my_player.zone  # @UndefinedVariable
        new_player.chp = jsonData[0]['chp']
        g.view.model.players_list.append(new_player)  # @UndefinedVariable 
                
    def clean_players_list(self, jsonData):
        removed = (jsonData[0]['player_id'])
        print 'removed player: %s' % removed

        for player in g.view.model.players_list:  # @UndefinedVariable
            if player.id == removed:
                g.view.model.players_list.remove(player)  # @UndefinedVariable
            
        
    def mob_update(self, jsonData):
        if jsonData[0]["zone"] == g.view.model.my_player.zone:  # @UndefinedVariable
            for mob in g.view.model.mob_list:  # @UndefinedVariable
                if mob.name == jsonData[0]['name']:
                    mob.x = jsonData[0]['x']
                    mob.y = jsonData[0]['y']
                    mob.chp = jsonData[0]['chp']
                    mob.mhp = jsonData[0]['mhp'] 
                    mob.dir = jsonData[0]['direction']
                    return
            new_mob = newmob.NewMob(jsonData[0]['name'], jsonData[0]['x'], jsonData[0]['y'], jsonData[0]['chp'], jsonData[0]['mhp'], jsonData[0]['direction'] ) 
            g.view.model.mob_list.append(new_mob)  # @UndefinedVariable
                          
                                               
    def mob_died(self, jsonData):
        print 'You got %s gold!' % (jsonData[0]['gold'])
        g.view.model.my_player.gold += jsonData[0]['gold'] / len(g.view.model.players_list)  # @UndefinedVariable
        name = jsonData[0]['name']
        for mob in g.view.model.mob_list:  # @UndefinedVariable
            if mob.name == name:
                g.view.model.mob_list.remove(mob)  # @UndefinedVariable

    def mob_attacked(self, jsonData):
        g.view.model.my_player.chp -= jsonData[0]['damage']
        g.tcpConn.sendHealthUpdate(g.view.model.my_player.chp, g.view.model.my_player.mhp)  # @UndefinedVariable
        print 'You took %d damage' % (jsonData[0]['damage'])
            
    def init_player(self, jsonData):
        g.view.model.id = jsonData[0]['player_id']
    
