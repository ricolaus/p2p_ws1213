import Queue
import time
import sys
import threading
# import copy

from overlay import Overlay
from application import Application
from network import Network



n2o = Queue.Queue()
o2n = Queue.Queue()
a2o = Queue.Queue()
o2a = Queue.Queue()
watcherQ = Queue.Queue()

argvLen = len(sys.argv)
print argvLen


if argvLen == 9:
    print "ok"
    userName = str(sys.argv[1])
    userFolder = str(sys.argv[2])
    ownIP = str(sys.argv[3])
    ownPort = int(sys.argv[4])
    bootstrapIP = str(sys.argv[5])
    bootstrapPort = int(sys.argv[6])
    TCPPortStart = int(sys.argv[7])
    TCPPortCount = int(sys.argv[8])
else:
    print "nisch ok"
    userName = "User1"          #str(argv[0])
    userFolder = "User1/"       #str(argv[1])
    ownIP = "localhost"         #str(argv[2])
    ownPort = 50001             #int(argv[3])
    bootstrapIP = "localhost"   #str(argv[4])
    bootstrapPort = 50000       #int(argv[5])
    TCPPortStart = 60010        #int(argv[6])
    TCPPortCount = 10           #int(argv[7])

# initialize and start overlay layer
overlay = Overlay(userName, ownIP, ownPort, bootstrapIP, bootstrapPort, n2o, o2n, a2o, o2a, watcherQ)
application = Application(userFolder, o2a, a2o)
network1 = Network(userFolder, ownIP, ownPort, TCPPortStart, TCPPortCount, n2o, o2n, watcherQ, 2)
network1.run()