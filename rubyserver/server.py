from twisted.internet.protocol import Factory
from twisted.internet import reactor, defer
from twisted.protocols.basic import LineReceiver
from twisted.internet.task import LoopingCall
from twisted.python import log
import json, base64
import time
from goblin import Goblin
from mobhandler import *
global dataHandler



class gameServerProtocol(LineReceiver):

    def __init__(self, factory):
        self.factory = factory
        self.zone = 1
        self.x = 0
        self.y = 0

    def connectionMade(self):
        self.factory.clients.append(self)
        dataHandler.init_player(self.factory.clients.index(self))
        print "A  player has joined"
        
    def connectionLost(self, reason):
        clientIndex = self.factory.clients.index(self)
        self.transport.loseConnection()
        dataHandler.clean_players_list(clientIndex)
        self.factory.clients[clientIndex].zone = 0
        print "Player %s has left" % clientIndex


    def lineReceived(self,data):
        global dataHandler
        clientIndex = self.factory.clients.index(self)
        decodedData = base64.b64decode(data)
        dataHandler.handleData(clientIndex, decodedData)

    def sendDataTo(self, index, data):
        # encode data using base64

        encodedData = base64.b64encode(data)

        self.factory.clients[index].sendLine(encodedData)

class gameServerFactory(Factory):
    protocol = gameServerProtocol

    def __init__(self):
        self.clients = []
        self.protocol = gameServerProtocol

    def buildProtocol(self, addr):
        self.proto = gameServerProtocol(self)
        return self.proto



    

class ServerPackets:
    SPlayerCoords,   \
    SCleanPlayersList,   \
    SMobUpdate,    \
    SMobDied,  \
    SMobAttacked,  \
    SInitPlayer,  \
    SHealthUpdate \
    = range(7)
    
class ClientPackets:
    CMoved, \
    CZone,     \
    CMobHit,   \
    CHealthUpdate \
    = range(4)
    
class DataHandler():
    def handleData(self, index, data):
        jsonData = json.loads(data)
        packetType = jsonData[0]["packet"]
        
        if packetType == ClientPackets.CMoved:
            self.client_moved(jsonData, index)
        elif packetType == ClientPackets.CHealthUpdate:
            self.health_update(jsonData, index)
        elif packetType == ClientPackets.CZone:
            self.zone_change(jsonData, index)
        elif packetType == ClientPackets.CMobHit:
            self.mob_hit(jsonData, index)
        elif packetType == ClientPackets.CInitPlayer:
            self.init_player(jsonData, index)
            
    def client_moved(self, jsonData, index):
        factory.clients[index].x = jsonData[0]['x']
        factory.clients[index].y = jsonData[0]['y']
        for i in range(0, len(factory.clients)):
            if factory.clients[i].zone == jsonData[0]['zone']:
                packet = json.dumps([{"packet": ServerPackets.SPlayerCoords, "player_id": index, "x": jsonData[0]['x'], "y": jsonData[0]['y'], "zone":jsonData[0]['zone'], "angle":jsonData[0]['angle'], "moving":jsonData[0]['moving']}])
                factory.proto.sendDataTo(i, packet)

    def health_update(self, jsonData, index):
        factory.clients[index].chp = jsonData[0]['chp']
        factory.clients[index].mhp = jsonData[0]['mhp']
        for i in range(0, len(factory.clients)):
            packet = json.dumps([{"packet": ServerPackets.SHealthUpdate, "player_id": index, "chp":factory.clients[index].chp, "mhp":factory.clients[index].mhp}])
            factory.proto.sendDataTo(i, packet)
        

    def zone_change(self, jsonData, index):
        factory.clients[index].zone = jsonData[0]['new_zone']
        self.clean_players_list(index)

        print 'zone change'

    def mob_hit(self, jsonData, index):
        for mob in loop.mob_handler.mob_list:
            if jsonData[0]['id'] == mob.name:
                mob.chp -= jsonData[0]['damage']
                if mob.x > factory.clients[index].x:
                    mob.xm = 10
                else:
                    mob.xm = -10
                if mob.y > factory.clients[index].y:
                    mob.ym = 10
                else:
                    mob.ym = -10
                if index not in mob.enemies:
                    mob.enemies.append(index)

    def init_player(self, index):
        packet = json.dumps([{"packet": ServerPackets.SInitPlayer, "player_id": index}])
        factory.proto.sendDataTo(index, packet)


    def clean_players_list(self, index): #remove this player from clients' player lists. used when changing zones, dc'ing, etc
        for i in range(0, len(factory.clients)):
            if i != index:
                packet = json.dumps([{"packet": ServerPackets.SCleanPlayersList, "player_id": index}])
                factory.proto.sendDataTo(i, packet)
    
class Main_Loop:    
    def __init__(self):
        self.mob_handler = MobHandler()


    def tick(self):
        self.mob_handler.handler(factory)

if __name__ == '__main__':
    global dataHandler, factory, loop
    dataHandler = DataHandler()
    factory = gameServerFactory()
    loop = Main_Loop()
    lc = LoopingCall(loop.tick)
    d = lc.start(.03)
    d.addErrback(log.err)
    reactor.listenTCP(6000, factory)
    #main loop here
    reactor.run()

