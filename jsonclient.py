from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from twisted.python import log
import view, base64
from datahandler import *  # @UnusedWildImport
import globalvars as g  # @Reimport


class gameClientProtocol(LineReceiver):
    def __init__(self, factory):
        self.factory = factory

    def lineReceived(self, data):
        global dataHandler
        decodedData = base64.b64decode(data)
        dataHandler.handleData(decodedData)

    def sendData(self, data):
        encodedData = base64.b64encode(data)
        self.sendLine(encodedData)
        


class gameClientFactory(ClientFactory):
    def __init__(self):
        self.protocol = gameClientProtocol(self)

    def buildProtocol(self, connector):
        return self.protocol


class TCPConnection():
    def __init__(self, protocol):
        self.protocol = protocol

    def sendData(self, data):
        self.protocol.sendData(data)

    def sendPlayerPos(self, x, y, zone, chp, mhp, angle, moving):
        packet = json.dumps([{"packet": ClientPackets.CMoved, "x": x, "y": y, "zone": zone, "angle":angle, "moving":moving}])
        self.sendData(packet)
        
    def sendZoneUpdate(self, new_zone, old_zone):
        packet = json.dumps([{"packet": ClientPackets.CZone, "new_zone": new_zone, "old_zone": old_zone}])
        self.sendData(packet)
        
    def sendHealthUpdate(self, chp, mhp):
        packet = json.dumps([{"packet": ClientPackets.CHealthUpdate, "chp": chp, "mhp": mhp}])
        self.sendData(packet)
        
    def sendMobHit(self, mob_id, damage):
        packet = json.dumps([{"packet": ClientPackets.CMobHit, "id": mob_id, "damage": damage}])
        self.sendData(packet)

if __name__ == '__main__':
    
    global dataHandler  
    factory = gameClientFactory()
    g.connector = reactor.connectTCP('127.0.0.1', 6000, factory)  # @UndefinedVariable
    g.view = view.View()
    g.tcpConn = TCPConnection(factory.protocol)
    dataHandler = DataHandler()
    #main loop here
    lc = LoopingCall(g.view.tick)  # @UndefinedVariable
    d = lc.start(.03)
    d.addErrback(log.err)
    reactor.run()  # @UndefinedVariable
    