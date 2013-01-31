import sys
import thread
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
        # list of all (5) neighbours
        self.neighbours = []
        # dictionary of received pings
        self.ping = {}
        # bool wether the program should terminate
        self.terminated = False
        # lock object for threads
        self.lock = thread.allocate_lock() 
        # number of active threads
        self.threadCount = 0
        # wether the thread was started or not
        self.threadStarted = False
        # ping to bootstrapping node
        self.putToOutQueue(("Ping", random.randrange(0, 9999, 1) , 4, 0, self.ownUsername, self.ownIP, bootstrappingIP))
    
    def terminate(self):
        print "Enter terminate()"
        self.terminated = True
    
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
            
    def processPing(self, message):
        # incoming Ping := ("Ping", PingID, TTL, Hops, senderUsername, senderIP)
        # outgoing Ping := ("Ping", PingID, TTL, Hops, ownUsername, ownIP, targetIP)
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
                if not neighbour == username:
                    self.putToOutQueue((msgType, id, ttl-1, hops+1, self.ownUsername, self.ownIP, self.neighbours[neighbour]))
        elif (ttl == 1) and (id not in self.ping):
            # add to ping dictionary
            self.ping[id] = ip
            # send pong to sender
            self.putToOutQueue(("Pong", id, [(self.ownUsername, self.ownIP)], self.ping[id]))
        else:
            print "Invalid ttl"
            
    def processPong(self, message):
        # incomingPong := ("Pong", ID, [(Username, IP), (Username2, IP2), ...])
        # outgoingPong := ("Pong", ID, [(Username, IP), (Username2, IP2), ...], IP)
        msgType, id, peers = message
        
        # refresh own peers list
        for peer in peers: 
            self.addToKnownPeers(peer)
        
        # add own identity to peers list
        if peers.count((self.ownUsername, self.ownIP)) == 0:
            peers.append((self.ownUsername, self.ownIP))
        
        # send pong to sender
        self.putToOutQueue((msgType, id, peers, self.ping[id]))

            
    def watchInQueue(self):
    
        self.lock.acquire()
        self.threadCount += 1
        self.threadStarted = True
        self.lock.release()
        
        print "Enter watchInQueue()"
        while not self.terminated:
            message = ()
            if not self.inQueue.empty():
                message = self.getFromInQueue()
                if message[0] == "Ping":
                    self.processPing(message)
                elif message[0] == "Pong":
                    self.processPong(message)
                else:
                    print "Unknown message type"
            # WARNING: the thread will terminate if the queue is empty
            # only for correct terminating while debugging
            else:
                self.terminated = True
        
        #if terminating
        self.lock.acquire()
        self.threadCount -= 1
        self.lock.release()
            
    def start(self):
        print "Enter start()"
        thread.start_new_thread(self.watchInQueue, ())
