import Queue
import time
import random
import threading
import pydot
import sys


from watcherNetwork import Network

n2w = Queue.Queue()
# {userName : ([(neighborUserName, currency), (...)], fileCount, color)
networkStructure = {}
peers = {}
lock = threading.Lock()
terminated = False

def colorList(i):
    r = i % 10
    g = (i//10) % 10
    b = (i//100) % 10
    if i > 500:
        fontColor = "#000000"
    else:
        fontColor = "#FFFFFF"
    return ("#%x" %(r*25) + "%x" %(g*25) + "%x" %(b*25), fontColor)

def addNewInformation():
    try:
        message = n2w.get(True, 1.0)
        fillColor, fontColor = colorList(random.randint(0, 999))
                      
        # neighbor message arrived
        if message[0] == "neighbors":
            userName, neighbors, fileCount = message[1:]
            fileCount = float(fileCount)
            
            # add to currency dictionary
            peers[userName] = 5
            
            if userName in networkStructure.keys():
                if fileCount == -1.0:
                    fileCount = networkStructure[userName][1]
                fillColor = networkStructure[userName][2]
                fontColor = networkStructure[userName][3]
                networkStructure[userName] = (neighbors, fileCount, fillColor, fontColor)
            else:
                networkStructure[userName] = (neighbors, fileCount, fillColor, fontColor)
        else:
            print "Message with unknown type arrived: " + message[0]
    except Queue.Empty:
        pass


def createGraph():
    # create a new digraph
    graph = pydot.Dot(graph_type='digraph')
    nodeDict = {}
    fileCount = ""
    
    for user in networkStructure.keys():
        if networkStructure[user][1] > -1.0:
            fileCount = " (" + "%.2f" % networkStructure[user][1] + ")"
        nodeName = user + fileCount
        # create and add node
        node = pydot.Node(nodeName, style="filled", fillcolor=networkStructure[user][2], fontcolor=networkStructure[user][3])
        # add to the dictionary
        nodeDict[user] = node 
        # add to the graph
        graph.add_node(node)
    for user in networkStructure.keys():
        # create an edge for every neighbor
        for neighbor in networkStructure[user][0]:
            # set edge style depending on currency
            edgeStyle = "solid"
            edgeColor = "black"
#            if neighbor[1] == 5:
#                edgeStyle = "bold"
#            if neighbor[1] == 4:
#                edgeStyle = "solid"
#            elif neighbor[1] == 3:
#                edgeStyle = "dashed"
#            elif neighbor[1] < 3:
#                edgeStyle = "dotted"
#                if neighbor[1] == 1 or neighbor[1] == 0:
#                    edgeStyle = "solid"
#                    edgeColor = "red"
            
            if neighbor[0] in nodeDict.keys():
                neighborNode = nodeDict[neighbor[0]]
            else:
                neighborNode = pydot.Node(neighbor[0], style="filled", color=edgeColor)
            # add the edge to the graph
            graph.add_edge(pydot.Edge(nodeDict[user], neighborNode, style=edgeStyle))
    try:
        # save the graph into a file
        graph.write_png('network.png')
    except Exception as msg:
        print "Failed to write network.png: " + str(msg)
    
    
def update():
    while not terminated:
        lock.acquire()
        addNewInformation()
        lock.release()
        
def writing():
    while not terminated:
        time.sleep(1)
        lock.acquire()
        createGraph()
        lock.release()
        
def checkCurrency():
    while not terminated:
        time.sleep(1)
        
        for name in peers.keys():
            if peers[name] > 0:
                peers[name] = peers[name] - 1
            else:
                if networkStructure.has_key(name):
                    networkStructure.pop(name)
                peers.pop(name)
                    


argvLen = len(sys.argv)
if argvLen == 2:
    watcherIP = str(sys.argv[1])
else:
    watcherIP = "localhost"     #str(argv[1])

# initialize and start network layer
network = Network(watcherIP, 1337, n2w)
network.run()

# start thread which creates the graph
currencyThread = threading.Thread(target=checkCurrency)
currencyThread.start()

# start thread which creates the graph
updateThread = threading.Thread(target=update)
updateThread.start()

# start thread which creates the graph
writingThread = threading.Thread(target=writing)
writingThread.start()

while not raw_input() == 'e':
    pass

network.terminate()
terminated = True

#n2w.put(("neighbors", "User1", [("User0", 1), ("User2", 2)]))
#time.sleep(2)
#n2w.put(("neighbors", "User0", [("User1", 0), ("User2", 5)]))
#time.sleep(2)
#n2w.put(("neighbors", "User2", [("User1", 3), ("User0", 4)]))
#time.sleep(2)
#n2w.put(("files", "User1", 2))
#time.sleep(2)
#n2w.put(("files", "User0", 2.5))
#time.sleep(2)
#n2w.put(("files", "User2", 2.5))