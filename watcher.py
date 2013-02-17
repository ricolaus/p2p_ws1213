import Queue
import time
import random
import threading
import pydot


from watcherNetwork import Network

n2m = Queue.Queue()
# {userName : ([(neighborUserName, currency), (...)], fileCount, color)
networkStructure = {}

def colorList(i):
    r = i % 10
    g = (i//10) % 10
    b = (i//100) % 10
    return "#%x" %(r*25) + "%x" %(g*25) + "%x" %(b*25)  

def addNewInformation():
    message = n2m.get(True)
    color = colorList(random.randint(200, 800))
                  
    # neighbor message arrived
    if message[0] == "neighbors":
        userName, neighbors = message[1:]
        if userName in networkStructure.keys():
            fileCount = networkStructure[userName][1]
            color =  networkStructure[userName][2]
            networkStructure[userName] = (neighbors, fileCount, color)
        else:
            networkStructure[userName] = (neighbors, -1, color)
    # file count message arrived
    elif message[0] == "files":
        userName, fileCount = message[1:]
        if userName in networkStructure.keys():
            neighbors = networkStructure[userName][0]
            color =  networkStructure[userName][2]
            networkStructure[userName] = (neighbors, fileCount, color)
        else:
            networkStructure[userName] = ([], -1, color)
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
            edgeStyle = "bold"
            if neighbor[1] == 4 or neighbor[1] == 5:
                edgeStyle = "solid"
            elif neighbor[1] == 2 or neighbor[1] == 3:
                edgeStyle = "dashed"
            elif neighbor[1] == 1 or neighbor[1] == 0:
                edgeStyle = "dotted"
            
            if neighbor[0] in nodeDict.keys():
                neighborNode = nodeDict[neighbor[0]]
            else:
                neighborNode = pydot.Node(neighbor[0] + " (-1)", style="filled")
            # add the edge to the graph
            graph.add_edge(pydot.Edge(nodeDict[user], neighborNode, style=edgeStyle))
    
    # save the graph into a file
    graph.write_png('network.png')
    
    
def update():
    while True:
        addNewInformation()
        createGraph()


# initialize and start network layer
network = Network("127.0.0.1", 1337, n2m)
network.run()

# start thread which creates the graph
updateThread = threading.Thread(target=update)
updateThread.start()

n2m.put(("neighbors", "User1", [("User0", 1), ("User2", 2)]))
time.sleep(2)
n2m.put(("neighbors", "User0", [("User1", 0), ("User2", 5)]))
time.sleep(2)
n2m.put(("neighbors", "User2", [("User1", 3), ("User0", 4)]))
time.sleep(2)
n2m.put(("files", "User1", 2))
time.sleep(2)
n2m.put(("files", "User0", 2.5))
time.sleep(2)
n2m.put(("files", "User2", 2.5))