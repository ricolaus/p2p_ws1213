from Queue import Queue
import time
# import sys
# import threading
# import copy


from overlay import Overlay
#import network


n2o = Queue()
o2n = Queue()
a2o = Queue()
o2a = Queue()

n2o.put(("ping", 1, 4, 0, "User1", 8.1, 81000), True)

# initialize and start overlay layer
overlay = Overlay("User0", 8.0, 80000, 1.337, 13370, n2o, o2n, a2o, o2a)

# n2o.put(("ping", 2, 2, 2, "User2", 8.2), True)
n2o.put(("pong", 1, [("User1", 8.1, 81000), ("User2", 8.2, 82000), ("User3", 8.3, 83000)]), True)
n2o.put(("pong", 1, [("User5", 8.5, 85000), ("User6", 8.6, 86000), ("User7", 8.7, 87000)]), True)
# wait until pong currency expired and pong has been sent
time.sleep(7)
n2o.put(("ping", 3, 1, 3, "User3", 8.3, 83000), True)
n2o.put(("ping", 4, 4, 0, "User4", 8.4, 84000), True)

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