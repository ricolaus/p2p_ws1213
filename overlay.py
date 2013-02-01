import threading, time
import random
# import sys
# import copy

class Overlay:
    def __init__(self, username, ip, bootstrappingIP, q1, q2, q3, q4):
        print "Enter constructor of overlay"
        # incoming queue from network layer
        self.n2o = q1
        # outgoing queue to network layer
        self.o2n = q2
        # incoming queue from application layer
        self.a2o = q3
        # outgoing queue to application layer
        self.o2a = q4
        # own username
        self.ownUsername = username
        # own ip
        self.ownIP = ip
        # list of known (max. 15) peers with structure: [(username, ip)]
        self.knownPeers = []
        # list of all (~5) neighbors with structure: [(username, ip, currency level)]
        self.neighbors = []
        # dictionary of received pings
        # TODO: change to list with currency levels
        self.ping = {}
        # bool whether the program should terminate
        self.__terminated = False
        # ping to bootstrapping node
        self.putToO2N(("ping", random.randint(0, 9999) , 4, 0, self.ownUsername, self.ownIP, bootstrappingIP))
        # start thread which watches the incoming queue from network layer
        self.n2oThread = threading.Thread(target=self.watchN2O)
        self.n2oThread.start()
        # start thread which checks the currency for the neighbors
        self.currencyThread = threading.Thread(target=self.checkCurrency)
        self.currencyThread.start()
        # start thread which watches the incoming queue from application layer
        self.a2oThread = threading.Thread(target=self.watchA2O)
        self.a2oThread.start()
    
    def terminate(self):
        print "Enter terminate()"
        self.__terminated = True
    
    def getFromN2O(self):
        print "Enter getFromN2O()"
        message = ()
        if self.n2o:
            message = self.n2o.get(True)
        return message
       
    def putToO2N(self, message):
        print "Enter putToO2N()"
        if self.o2n:
            self.o2n.put(message, True)
            
    def getFromA2O(self):
        print "Enter getFromA2O()"
        message = ()
        if self.a2o:
            message = self.a2o.get(True)
        return message
       
    def putToO2A(self, message):
        print "Enter putToO2A()"
        if self.o2a:
            self.o2a.put(message, True)

    def addToKnownPeers(self, peer):
        if not peer == (self.ownUsername, self.ownIP):
            if self.knownPeers.count(peer) == 0:
                self.knownPeers.append(peer)
                if len(self.knownPeers) > 15:
                    self.knownPeers.pop(0)
                    
    def addToNeighbours(self, peer, currency):
        if (not peer == (self.ownUsername, self.ownIP)) and self.neighbors.count(peer) == 0 and len(self.neighbors) < 6:
            self.neighbors.append((peer[0], peer[1], currency))
            return True
        else:
            return False
                    
    def refreshNeighbours(self):
        number = 5
        if len(self.knownPeers) < 5:
            number = len(self.knownPeers)
            
        sample = random.sample(self.knownPeers, number) 
        for knownPeer in sample: 
            self.addToNeighbours(knownPeer, 2)

            
    def watchN2O(self):
        print "Enter watchN2O()"
        while not self.__terminated:
            message = ()
            if not self.n2o.empty():
                message = self.getFromN2O()
                if message[0] == "ping":
                    self.processping(message)
                    # print "Reenter watchN2O() from processping"
                elif message[0] == "pong":
                    self.processpong(message)
                    # print "Reenter watchN2O() from processpong"
                elif message[0] == "refFL":
                    self.processIncRefFL(message)
                else:
                    print "Unknown message type"
            
    def processping(self, message):
        # incoming ping := ("ping", pingID, TTL, Hops, senderUsername, senderIP)
        # outgoing ping := ("ping", pingID, TTL, Hops, ownUsername, ownIP, targetIP)
        
        print "Enter processping()"
        
        msgType, msgID, ttl, hops, username, ip = message
        
        # add to/refresh knownPeers list
        self.addToKnownPeers((username, ip))
        
        if (ttl > 1) and (msgID not in self.ping):
            # add to ping dictionary
            self.ping[msgID] = ip
            # if ttl is to high
            if ttl + hops > 7:
                ttl = 7 - hops
            # send ping to each neighbor
            for neighbor in self.neighbors: 
                if not neighbor[0] == username:
                    self.putToO2N((msgType, msgID, ttl-1, hops+1, self.ownUsername, self.ownIP, neighbor[1]))
        elif (ttl == 1) and (msgID not in self.ping):
            # add to ping dictionary
            self.ping[msgID] = ip
            # send pong to sender
            self.putToO2N(("pong", msgID, [(self.ownUsername, self.ownIP)], self.ping[msgID]))
        else:
            print "Invalid ttl"
            
    def processpong(self, message):
        # incoming pong := ("pong", ID, [(Username, IP), (Username2, IP2), ...])
        # outgoing pong := ("pong", ID, [(Username, IP), (Username2, IP2), ...], IP)
        
        print "Enter processpong()"
        
        msgType, msgID, peers = message
        
        # refresh own peers list
        for peer in peers: 
            self.addToKnownPeers(peer)
        
        # add own identity to peers list
        if peers.count((self.ownUsername, self.ownIP)) == 0:
            peers.append((self.ownUsername, self.ownIP))
        
        # send pong to sender
        if msgID in self.ping:
            self.putToO2N((msgType, msgID, peers, self.ping[msgID]))
        else:
            print "Cannot forward pong because no ping with this id has arrived before"

        # refresh/fill neighbor list
        self.refreshNeighbours()

      
    def checkCurrency(self):
        print "Enter checkCurrency()"
        
        while not self.__terminated:
            
            time.sleep(2)
            
            tmp = self.neighbors
            for neighbor in tmp:
                if neighbor[2] > 0:
                    self.neighbors.append((neighbor[0], neighbor[1], neighbor[2] - 1))
                self.neighbors.remove(neighbor)
                
        
    def watchA2O(self):
        print "Enter watchA2O()"
        while not self.__terminated:
            message = ()
            if not self.a2o.empty():
                message = self.getFromA2O()
                if message[0] == "refFL":
                    self.processOutRefFL(message)
                elif message[0] == "reqFile":
                    pass
                    # self.processReqFile(message)
                elif message[0] == "answerReg":
                    pass
                    # self.processAnswerReg(message)
                else:
                    print "Unknown message type"
        
        
    def processIncRefFL(self, message):
        print "Enter processIncRefFL()"
        
        msgType, fileList, senderUsername, senderIP = message
        
        if (senderUsername, senderIP) in self.neighbors:
            self.putToO2A((msgType, fileList, senderUsername, False))
        elif self.addToNeighbours((senderUsername, senderIP), 5):
            self.putToO2A((msgType, fileList, senderUsername, True))
        
        
        
    def processOutRefFL(self, message):
        print "Enter processOutRefFL()"
        
        msgType, fileList = message
        
        for neighbor in self.neighbors:
            self.putToO2N((msgType, fileList, self.ownUsername, neighbor[1]))

        
        
        
        
        
        
        
        
        
        
