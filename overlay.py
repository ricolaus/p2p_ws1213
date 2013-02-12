import threading, time
import random
# import sys
# import copy

class Overlay:
    #===========================================================================
    # __init__
    #
    # Constructor of the overlay layer.
    # Initializes all class variables.
    # Sends the first (bootstrapping) 'ping' message.
    # Starts all threads.
    #===========================================================================
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
        # dictionary of received pings with structure: {msgID: (ip, currency level)}
        self.pingDict = {}
        # dictionary of received pongs with structure: {msgID: (ip, set((username, ip), ...), currency level)}
        self.pongDict = {}
        # bool whether the program should terminate
        self.__terminated = False
        # ping to bootstrapping node
        self.putToO2N(("ping", random.randint(0, 9999) , 4, 0, self.ownUsername, self.ownIP, bootstrappingIP))
        # start thread which watches the incoming queue from network layer
        self.n2oThread = threading.Thread(target=self.watchN2O)
        self.n2oThread.start()
        # start thread which checks the currency for the neighbors
        self.neighborCurrencyThread = threading.Thread(target=self.checkNeighborCurrency)
        self.neighborCurrencyThread.start()
        # start thread which watches the incoming queue from application layer
        self.a2oThread = threading.Thread(target=self.watchA2O)
        self.a2oThread.start()
        # start thread which checks the currency for the pings
        self.pingPongCurrencyThread = threading.Thread(target=self.checkPingPongCurrency)
        self.pingPongCurrencyThread.start()
    
    #===========================================================================
    # terminate
    #
    # Initiates the termination of all threads.
    #===========================================================================
    def terminate(self):
        print "Enter terminate()"
        self.__terminated = True
    
    #===========================================================================
    # getFromN2O
    #
    # Gets a message from the incoming queue from the network.
    #===========================================================================
    def getFromN2O(self):
        print "Enter getFromN2O()"
        message = ()
        if self.n2o:
            message = self.n2o.get(True)
        return message
       
    #===========================================================================
    # putToO2N
    #
    # Puts a message into the outgoing queue to the network.
    #===========================================================================
    def putToO2N(self, message):
        print "Enter putToO2N()"
        if self.o2n:
            self.o2n.put(message, True)
            
    #===========================================================================
    # getFromA2O
    #
    # Gets a message from the incoming queue from the application.
    #===========================================================================
    def getFromA2O(self):
        print "Enter getFromA2O()"
        message = ()
        if self.a2o:
            message = self.a2o.get(True)
        return message
       
    #===========================================================================
    # putToO2A
    #
    # Puts a message into the outgoing queue to the application.
    #===========================================================================
    def putToO2A(self, message):
        print "Enter putToO2A()"
        if self.o2a:
            self.o2a.put(message, True)

    #===========================================================================
    # addToKnownPeers
    #
    # Adds the passed peer  to the known peers list.
    # Removes the first peer in if the list has more than 15 elements.  
    #===========================================================================
    def addToKnownPeers(self, peer):
        if not peer == (self.ownUsername, self.ownIP):
            if self.knownPeers.count(peer) == 0:
                self.knownPeers.append(peer)
                if len(self.knownPeers) > 15:
                    self.knownPeers.pop(0)
                    
    #===========================================================================
    # addToNeighbours
    #
    # Adds the passed peer with its currency to the neighbor list.
    # Returns:
    # True, if the peer was added
    # False, else
    #===========================================================================
    def addToNeighbours(self, peer, currency):
        if (not peer == (self.ownUsername, self.ownIP)) and self.neighbors.count(peer) == 0 and len(self.neighbors) < 6:
            self.neighbors.append((peer[0], peer[1], currency))
            return True
        else:
            return False
                    
    #===========================================================================
    # refreshNeighbours
    #
    # Trys to add max. 5 of the known peers to the neighbor list.
    #===========================================================================
    def refreshNeighbours(self):
        number = 5
        if len(self.knownPeers) < 5:
            number = len(self.knownPeers)
            
        sample = random.sample(self.knownPeers, number) 
        for knownPeer in sample: 
            self.addToNeighbours(knownPeer, 2)

    #===========================================================================
    # watchN2O
    #
    # Watches the incoming queue from the network layer.
    #===========================================================================
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
                elif message[0] == "reqFile":
                    pass
                    # TODO:
                    # self.processReqFile(message)
                elif message[0] == "answerReq":
                    pass
                    # TODO:
                else:
                    print "Unknown message type"
            
    #===========================================================================
    # processping
    #
    # Processes the incoming 'ping' message.
    # If TTL is high enough a ping is sent to all neighbors.
    # If TTL = 1 a pong is sent to the sender of the ping.
    #===========================================================================
    def processping(self, message):
        # incoming ping := ("ping", pingID, TTL, Hops, senderUsername, senderIP)
        # outgoing ping := ("ping", pingID, TTL, Hops, ownUsername, ownIP, targetIP)
        
        print "Enter processping()"
        
        msgType, msgID, ttl, hops, username, ip = message
        
        # add to/refresh knownPeers list
        self.addToKnownPeers((username, ip))
        
        if (ttl > 1) and (msgID not in self.pingDict):
            # add to ping dictionary
            self.pingDict[msgID] = (ip, ttl)
            # if ttl is to high
            if ttl + hops > 7:
                ttl = 7 - hops
            # send ping to each neighbor
            for neighbor in self.neighbors: 
                if not neighbor[0] == username:
                    self.putToO2N((msgType, msgID, ttl-1, hops+1, self.ownUsername, self.ownIP, neighbor[1]))
        elif (ttl == 1) and (msgID not in self.pingDict):
            # add to ping dictionary
            self.pingDict[msgID] = (ip, ttl)
            # send pong to sender
            self.putToO2N(("pong", msgID, [(self.ownUsername, self.ownIP)], self.pingDict[msgID][0]))
        elif (msgID in self.pingDict):
            print "Already got a ping entry with this message ID"
        else:
            print "Invalid ttl"
            
    #===========================================================================
    # processpong
    #
    # Processes the incoming 'pong' message.
    # Adds own identity to the message and sends it to the former sender of the
    # ping message. Then trys to fill the neighbor list.
    #===========================================================================
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
        
        peerSet = set()
        for peer in peers:
            peerSet.add(peer)
        
        # save pong in pongDict
        if msgID in self.pingDict:
            # add new pong message with ip set of peers and currency level
            self.pongDict[msgID] = (self.pingDict[msgID][0], peerSet, 5)
            self.pingDict.pop(msgID)
        elif msgID in self.pongDict:
            # add peers from further pong messages to peerSet
            for p in self.pongDict[msgID][1]:
                peerSet.add(p)
            # add new pong message with ip set of peers and currency level
            self.pongDict[msgID] = (self.pongDict[msgID][0], peerSet, self.pongDict[msgID][2])
        else:
            print "Cannot save pong because no ping with this id has arrived before"

      
    #===========================================================================
    # checkNeighborCurrency
    #
    # Checks periodically whether the currency level of all neighbors is greater
    # zero. If not the neighbor is removed.
    #===========================================================================
    def checkNeighborCurrency(self):
        print "Enter checkNeighborCurrency()"
        
        while not self.__terminated:
            
            time.sleep(2)
            
            tmp = self.neighbors
            for neighbor in tmp:
                if neighbor[2] > 0:
                    self.neighbors.append((neighbor[0], neighbor[1], neighbor[2] - 1))
                self.neighbors.remove(neighbor)
                
    #===========================================================================
    # checkPingPongCurrency
    #
    # Checks periodically whether the currency level of all pings is greater
    # zero. If not the ping is removed.
    #===========================================================================
    def checkPingPongCurrency(self):
        print "Enter checkPingPongCurrency()"
        
        while not self.__terminated:
            
            time.sleep(1)
            
            tmp = self.pingDict
            for key in tmp.keys():
                if self.pingDict[key][1] > 0:
                    self.pingDict[key] = (self.pingDict[key][0], self.pingDict[key][1] - 1)
                else:
                    self.pingDict.pop(key)
                    
            tmp = self.pongDict
            for key in tmp.keys():
                if self.pongDict[key][2] > 0:
                    self.pongDict[key] = (self.pongDict[key][0], self.pongDict[key][1], self.pongDict[key][2] - 1)
                else:
                    # finally send pong message
                    self.putToO2N(("pong", key, self.pongDict[key][1], self.pongDict[key][0]))
                    # refresh/fill neighbor list
                    self.refreshNeighbours()
                    # remove from dictionary
                    self.pongDict.pop(key)                    
        
    #===========================================================================
    # watchA2O
    #
    # Watches the incoming queue from the application layer.
    #===========================================================================
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
                    # TODO:
                    # self.processReqFile(message)
                elif message[0] == "answerReq":
                    pass
                    # TODO:
                    # self.processAnswerReg(message)
                else:
                    print "Unknown message type"
        
    #===========================================================================
    # processIncRefFL
    #
    # Processes the incoming 'refresh file list' message from network layer.
    # Trys to add peer to neighbors if he is not already one.
    # If adding has success an urgent answer from application layer is requested.
    #===========================================================================
    def processIncRefFL(self, message):
        print "Enter processIncRefFL()"
        
        msgType, fileList, senderUsername, senderIP = message
        
        if (senderUsername, senderIP) in self.neighbors:
            self.putToO2A((msgType, fileList, senderUsername, False))
        elif self.addToNeighbours((senderUsername, senderIP), 5):
            self.putToO2A((msgType, fileList, senderUsername, True))

    #===========================================================================
    # processOutRefFL
    #
    # Processes the outgoing 'refresh file list' message to network layer.
    # Sends the message to all neighbors.
    #===========================================================================
    def processOutRefFL(self, message):
        print "Enter processOutRefFL()"
        
        msgType, fileList = message
        
        for neighbor in self.neighbors:
            self.putToO2N((msgType, fileList, self.ownUsername, neighbor[1]))

        
        
        
        
        
        
        
        
        
        
