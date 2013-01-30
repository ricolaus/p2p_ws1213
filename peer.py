import sys
from Queue import Queue
#import copy

from overlay import Overlay
#import network


inQueue = Queue()
outQueue = Queue()

test = ("Ping", "User" ,8.2)

inQueue.put(test)

overlay = Overlay(inQueue, outQueue)
overlay.start()
#outQueue.put(number)

##while not inQueue.empty():
##    print inQueue.get()
##print "/"
while not outQueue.empty():
    print outQueue.get()
