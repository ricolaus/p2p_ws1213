import Queue
import time
import random
import threading
import pydot


from watcherNetwork import Network

n2w = Queue.Queue()
# {userName : ([(neighborUserName, currency), (...)], fileCount, color)
networkStructure = {}
peers = {}
lock = threading.Lock()

def colorList(i):
    r = i % 10
    g = (i//10) % 10
    b = (i//100) % 10
    return "#%x" %(r*25) + "%x" %(g*25) + "%x" %(b*25)  

def addNewInformation():
    message = n2w.get(True)
    color = colorList(random.randint(200, 800))
                  
    # neighbor message arrived
    if message[0] == "neighbors":
        userName, neighbors, fileCount = message[1:]
        # add to currency dictionary
        peers[userName] = 5
        
        if userName in networkStructure.keys():
            if fileCount == '-1':
                fileCount = networkStructure[userName][1]
            color =  networkStructure[userName][2]
            networkStructure[userName] = (neighbors, fileCount, color)
        else:
            networkStructure[userName] = (neighbors, fileCount, color)
    else:
        print "Message with unknown type arrived: " + message[0]


def createGraph():
    # create a new digraph
    graph = pydot.Dot(graph_type='digraph')
    nodeDict = {}
    
    for user in networkStructure.keys():
        nodeName = user + " (" + str(networkStructure[user][1]) + ")"
        # create and add node
        node = pydot.Node(nodeName, style="filled", fillcolor=networkStructure[user][2])
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
                neighborNode = pydot.Node(neighbor[0] + " (-1)", style="filled", color=edgeColor)
            # add the edge to the graph
            graph.add_edge(pydot.Edge(nodeDict[user], neighborNode, style=edgeStyle))
    try:
        # save the graph into a file
        graph.write_png('network.png')
    except Exception as msg:
        print "Failed to write network.png: " + str(msg)
    
    
def update():
    while True:
        lock.acquire()
        addNewInformation()
        lock.release()
        
def writing():
    while True:
        time.sleep(1)
        lock.acquire()
        createGraph()
        lock.release()
        
def checkCurrency():
    while True:
        time.sleep(1)
        
        for name in peers.keys():
            if peers[name] > 0:
                peers[name] = peers[name] - 1
            else:
                if networkStructure.has_key(name):
                    networkStructure.pop(name)
                peers.pop(name)
                    


# initialize and start network layer
network = Network("127.0.0.1", 1337, n2w)
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