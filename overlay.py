import sys
#import copy

class Overlay:
    def __init__(self, q1=None, q2=None):
        # Das sind die Queue Elemente
        self.inQueue = q1
        self.outQueue = q2
        # dictionary of all neighbours
        self.neighbours = {}

        self.to = 1 # queue-timeout

    def getFromInQueue(self):
        obj = ()
        if self.inQueue:
            obj = self.inQueue.get(timeout=self.to)
        return obj
       
    def putToOutQueue(self, obj):
        if self.outQueue:
            self.outQueue.put(obj, timeout=self.to)
            
    def start(self):
        obj = ()
        obj = self.getFromInQueue()
        self.neighbours[obj[1]] = obj[2]
        self.putToOutQueue(self.neighbours)