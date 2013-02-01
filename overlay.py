import sys
import threading
import random
#import copy

class Overlay:
    def __init__(self, username, ip, bootstrappingIP, q1=None, q2=None):
        print "Enter constructor of overlay"
        # incoming queue
        self.inQueue = q1
        # outgoing queue
        self.outQueue = q2
        # own username
        self.ownUsername = username
        # own ip
        self.ownIP = ip
        # list of known (max. 15) peers
        self.knownPeers = []
        # list of all (~5) neighbours
        self.neighbours = []
        # dictionary of received pings
        self.ping = {}
        # bool wether the program should terminate
        self.__terminated = False
        # ping to bootstrapping node
        self.putToOutQueue(("ping", random.randint(0, 9999) , 4, 0, self.ownUsername, self.ownIP, bootstrappingIP))
        # start thread which watches the incoming queue
        self.inQueueThread = threading.Thread(target=self.watchInQueue)
        self.inQueueThread.start()
    
    def terminate(self):
        print "Enter terminate()"
        self.__terminated = True
    
    def getFromInQueue(self):
        print "Enter getFromInQueue()"
        message = ()
        if self.inQueue:
            message = self.inQueue.get(True)
        return message
       
    def putToOutQueue(self, message):
        print "Enter putToOutQueue()"
        if self.outQueue:
            self.outQueue.put(message, True)

    def addToKnownPeers(self, peer):
        if not peer == (self.ownUsername, self.ownIP):
            if self.knownPeers.count(peer) == 0:
                self.knownPeers.append(peer)
                if len(self.knownPeers) > 15:
                    self.knownPeers.pop(0)
                    
    def addToNeighbours(self, peer):
        if not peer == (self.ownUsername, self.ownIP):
            if self.neighbours.count(peer) == 0:
                if len(self.neighbours) < 5:
                    self.neighbours.append(peer)
                    
    def refreshNeighbours(self):
        number = 5
        if len(self.knownPeers) < 5:
            number = len(self.knownPeers)
            
        sample = random.sample(self.knownPeers, number) 
        for knownPeer in sample: 
            self.addToNeighbours(knownPeer)

            
    def processping(self, message):
        # incoming ping := ("ping", pingID, TTL, Hops, senderUsername, senderIP)
        # outgoing ping := ("ping", pingID, TTL, Hops, ownUsername, ownIP, targetIP)
        
        print "Enter processping()"
        
        msgType, id, ttl, hops, username, ip = message
        
        # add to/refresh knownPeers list
        self.addToKnownPeers((username, ip))
        
        if (ttl > 1) and (id not in self.ping):
            # add to ping dictionary
            self.ping[id] = ip
            # if ttl is to high
            if ttl + hops > 7:
                ttl = 7 - hops
            # send ping to each neighbour
            for neighbour in self.neighbours: 
                if not neighbour[0] == username:
                    self.putToOutQueue((msgType, id, ttl-1, hops+1, self.ownUsername, self.ownIP, neighbour[1]))
        elif (ttl == 1) and (id not in self.ping):
            # add to ping dictionary
            self.ping[id] = ip
            # send pong to sender
            self.putToOutQueue(("pong", id, [(self.ownUsername, self.ownIP)], self.ping[id]))
        else:
            print "Invalid ttl"
            
    def processpong(self, message):
        # incomingpong := ("pong", ID, [(Username, IP), (Username2, IP2), ...])
        # outgoingpong := ("pong", ID, [(Username, IP), (Username2, IP2), ...], IP)
        
        print "Enter processpong()"
        
        msgType, id, peers = message
        
        # refresh own peers list
        for peer in peers: 
            self.addToKnownPeers(peer)
        
        # add own identity to peers list
        if peers.count((self.ownUsername, self.ownIP)) == 0:
            peers.append((self.ownUsername, self.ownIP))
        
        # send pong to sender
        if id in self.ping:
            self.putToOutQueue((msgType, id, peers, self.ping[id]))
        else:
            print "Cannot forward pong because no ping with this id has arrived before"

        # refresh/fill neighbour list
        self.refreshNeighbours()
        
            
    def watchInQueue(self):
        print "Enter watchInQueue()"
        while not self.__terminated:
            message = ()
            if not self.inQueue.empty():
                message = self.getFromInQueue()
                if message[0] == "ping":
                    self.processping(message)
                    # print "Reenter watchInQueue() from processping"
                elif message[0] == "pong":
                    self.processpong(message)
                    # print "Reenter watchInQueue() from processpong"
                else:
                    print "Unknown message type"
            # WARNING: the thread will terminate if the queue is empty
            # only for correct terminating while debugging
            # else:
                # self.__terminated = True
                
            
    def start(self):
        print "Enter start()"
