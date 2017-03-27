from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.defer import setDebugging
import view

class ChatClientProtocol(LineReceiver):

    def __init__(self, recv):
        self.recv = recv

    def lineReceived(self,line):
        view.model.line = line
        self.recv(line)

    def dataReceived(self, data):

        data = data.split("!")
        for i, player in enumerate(data):
            data[i] = player.split(",")
        data.pop(len(data) - 1)     
        if 'player' in data[0][0]:
            view.model.players_and_mobs_update(data)  # @UndefinedVariable
        if 'static' in data[0][0]:
            view.model.static_update(data) # @UndefinedVariable
    def sendLine(self, line):
        self.transport.write(line)

    def connectionMade(self):
        self.sendLine("connection made")


class ChatClient(ClientFactory):
    def __init__(self, client):
        self.client = client
        self.protocol = ChatClientProtocol
    def buildProtocol(self, addr):
        self.proto = ChatClientProtocol(self.client)
        return self.proto

if __name__ == '__main__':

    setDebugging(True)
    view = view.View()
    view.factory = ChatClient(view.model.new_line)
    lc = LoopingCall(view.tick)
    lc.start(.03)
    reactor.connectTCP('127.0.0.1',6000, view.factory)    # @UndefinedVariable
    reactor.run()  # @UndefinedVariable
    while True:
        view.tick()