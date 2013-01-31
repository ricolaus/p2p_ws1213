import sys
from Queue import Queue
import threading
#import copy

from overlay import Overlay
#import network


inQueue = Queue()
outQueue = Queue()

inQueue.put(("Ping", 1, 4, 0, "User1", 8.1), True)

# initialize and start overlay layer
overlay = Overlay("User0", 8.0, 1.337, inQueue, outQueue)
# overlay.start()

inQueue.put(("Ping", 2, 2, 2, "User2", 8.2), True)
inQueue.put(("Pong", 1, [("User1", 8.1), ("User2", 8.2), ("User3", 8.3)]), True)
inQueue.put(("Ping", 3, 1, 3, "User3", 8.3), True)
inQueue.put(("Ping", 4, 4, 0, "User4", 8.4), True)

while not inQueue.empty():
    pass

overlay.terminate()
overlay.inQueueThread.join()
    
# debug output
print "Number of processed messages: " + str(outQueue.qsize())
while not outQueue.empty():
    print outQueue.get(True)

# overlay.terminate()