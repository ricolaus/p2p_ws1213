from __future__ import print_function
import Queue
import time
import sys
import threading
# import copy

from overlay import Overlay
from application import Application
from network import Network

# nice, cheap and dirty hack for a thread safe print function
print = lambda x: sys.stdout.write("%s\n" % x)


#===============================================================================
# transfer
#
# Function for debugging purposes.
# Allows to transfer messages between TWO(!) peers without the network layer.
# Peers have to be    User0 with IP 8.0 and Port 80000
#                     and
#                     User1 with IP 8.1 and Port 81000.
#===============================================================================
def transfer(q1, q2):
    while True:
        message = q1.get(True)
        print(str(message))
        
        # refFL
        if message[0] == "refFL":
            msgType, fileList, senderUsername, senderIP, senderPort, targetIP, targetPort = message
            q2.put((msgType, fileList, senderUsername, senderIP, senderPort), True)
            
        # ping
        if message[0] == "ping":
            msgType, msgID, ttl, hops, username, ip, port, targetIP, targetPort = message
            q2.put((msgType, msgID, ttl, hops, username, ip, port), True)
            
        # pong
        if message[0] == "pong":
            msgType, msgID, origPeers, targetIP, targetPort  = message
            q2.put((msgType, msgID, origPeers), True)
            
        #reqFile
        if message[0] == "reqFile":
            msgType, fileName, fileHash, senderIP, senderPort , targetIP, targetPort = message
            q2.put((msgType, fileName, fileHash, senderIP, senderPort, 60000), True)


n2o = Queue.Queue()
o2n = Queue.Queue()
a2o = Queue.Queue()
o2a = Queue.Queue()

a2otmp = Queue.Queue()
o2atmp = Queue.Queue()
n2otmp = Queue.Queue()
o2ntmp = Queue.Queue()

#transferThread1 = threading.Thread(target=transfer, args=(o2n, n2otmp))
#transferThread1.start()
#
#transferThread2 = threading.Thread(target=transfer, args=(o2ntmp, n2o))
#transferThread2.start()

#n2o.put(("ping", 1, 4, 0, "User1", 8.1, 81000), True)
#n2otmp.put(("ping", 1, 4, 0, "User0", 8.0, 80000), True)

# initialize and start overlay layer
overlay = Overlay("User0", "localhost", 50000, "localhost", 13370, n2o, o2n, a2o, o2a)
#application = Application("C:/Users/Skid/Desktop/Uni/11. Semester/P2P/Folder Sync/User0", o2a, a2o)
application = Application("User0/", o2a, a2o)
network1 = Network("localhost", 50001, 50000, 60000, 10, n2o, o2n, 2)
network1.run()






time.sleep(3)

overlay2 = Overlay("User1", "localhost", 50001, "localhost", 50000, n2otmp, o2ntmp, a2otmp, o2atmp)
#application2 = Application("C:/Users/Skid/Desktop/Uni/11. Semester/P2P/Folder Sync/User1", o2atmp, a2otmp)
application2 = Application("User1/", o2atmp, a2otmp)
network2 = Network("localhost", 50000, 50001, 60010, 10, n2otmp, o2ntmp, 2)
network2.run()

# n2o.put(("ping", 2, 2, 2, "User2", 8.2), True)
#n2o.put(("pong", 1, [("User2", 8.2, 82000), ("User3", 8.3, 83000), ("User4", 8.4, 84000)]), True)
#n2o.put(("pong", 1, [("User5", 8.5, 85000), ("User6", 8.6, 86000), ("User7", 8.7, 87000)]), True)
# wait until pong currency expired and pong has been sent
#time.sleep(7)
#n2o.put(("ping", 3, 1, 3, "User3", 8.3, 83000), True)
#n2o.put(("ping", 4, 4, 0, "User4", 8.4, 84000), True)

#a2o.put(("refFL", [("File1", 800), ("File2", 600)]))
#n2o.put(("refFL", {('1.txt', '0cbc6611f5540bd0709a388dc95a615b'): ([], 4L, 1360778641.997759, 0)}, "User1", 8.1, 81000))
#while not n2o.empty():
#    pass
#
#overlay.terminate()
#overlay.n2oThread.join()
#overlay.neighborCurrencyThread.join()
#overlay.a2oThread.join()
#overlay.pingPongCurrencyThread.join()
    
# debug output
#while True:#not o2n.empty():
#    print "User0:" + str(o2n.get())
#    print "User1:" + str(o2ntmp.get())