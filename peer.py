import sys
from Queue import Queue
import threading
#import copy

from overlay import Overlay
#import network


inQueue = Queue()
outQueue = Queue()

inQueue.put(("Ping", "0001", 4, 0, "User1", 8.1), True)

# initialize and start overlay layer
overlay = Overlay("User0", 8.0, 1.337, inQueue, outQueue)
overlay.start()

inQueue.put(("Ping", "0002", 2, 0, "User2", 8.2), True)
inQueue.put(("Ping", "0003", 1, 0, "User3", 8.3), True)

while not inQueue.empty():
    pass

overlay.terminate()
    
# debug output
print "Number of processed messages: " + str(outQueue.qsize())
while not outQueue.empty():
    print outQueue.get(True)

# overlay.terminate()