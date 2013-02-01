from Queue import Queue
# import sys
# import threading
# import copy

from overlay import Overlay
#import network


n2o = Queue()
o2n = Queue()
a2o = Queue()
o2a = Queue()

n2o.put(("ping", 1, 4, 0, "User1", 8.1), True)

# initialize and start overlay layer
overlay = Overlay("User0", 8.0, 1.337, n2o, o2n, a2o, o2a)

# n2o.put(("ping", 2, 2, 2, "User2", 8.2), True)
n2o.put(("pong", 1, [("User1", 8.1), ("User2", 8.2), ("User3", 8.3)]), True)
n2o.put(("pong", 1, [("User5", 8.5), ("User6", 8.6), ("User7", 8.7)]), True)
n2o.put(("ping", 3, 1, 3, "User3", 8.3), True)
n2o.put(("ping", 4, 4, 0, "User4", 8.4), True)

a2o.put(("refFL", [("File1", 800), ("File2", 600)]))

while not n2o.empty():
    pass

overlay.terminate()
overlay.n2oThread.join()
overlay.neighborCurrencyThread.join()
overlay.a2oThread.join()
overlay.pingPongCurrencyThread.join()
    
# debug output
while not o2n.empty():
    print o2n.get(True)