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


n2o = Queue.Queue()
o2n = Queue.Queue()
a2o = Queue.Queue()
o2a = Queue.Queue()

userName = "User0"
userFolder = "User0/"
ownIP = "localhost"
ownPort = 50000
bootstrapIP = "localhost"
bootstrapPort = 13370
TCPPortStart = 60000
TCPPortCount = 10

# initialize and start overlay layer
overlay = Overlay(userName, ownIP, ownPort, bootstrapIP, bootstrapPort, n2o, o2n, a2o, o2a)
application = Application(userFolder, o2a, a2o)
network1 = Network(userFolder, ownIP, ownPort, TCPPortStart, TCPPortCount, n2o, o2n, 2)
network1.run()


time.sleep(2.5)

a2otmp = Queue.Queue()
o2atmp = Queue.Queue()
n2otmp = Queue.Queue()
o2ntmp = Queue.Queue()

user1Folder = "User1/"
overlay2 = Overlay("User1", "localhost", 50001, "localhost", 50000, n2otmp, o2ntmp, a2otmp, o2atmp)
#application2 = Application("C:/Users/Skid/Desktop/Uni/11. Semester/P2P/Folder Sync/User1", o2atmp, a2otmp)
application2 = Application(user1Folder, o2atmp, a2otmp)
network2 = Network(user1Folder, "localhost", 50001, 60010, 10, n2otmp, o2ntmp, 2)
network2.run()