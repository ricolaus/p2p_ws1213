import threading
from Queue import Queue
import time
import os

    
class Application:
    def __init__(self, q1=None, q2=None, q3=None):
        self.folderName = "/home/imon/Uni-11/P2P/Test"
        self.mainLoopTimeout = 10
        self.fileSet = set()
        #queue from and to overlay
        self.inQueue = q1 or Queue()      
        self.outQueue = q2 or Queue()
        #queue for user input, maybe not needed
        self.interfacequeue = q3 or Queue()
        self.mainLoopThread = threading.Thread(target=self.mainLoop)
        self.mainLoopThread.start()
        self.overlayWaitThread = threading.Thread(target=self.overlayWait)
        self.overlayWaitThread.start()
        #self.mainLoopThread.join()
       
    def mainLoop(self):
        n=1
        while(True):
            files = os.listdir(self.folderName)
            newFiles = set(files) - self.fileSet
            if len(newFiles) > 0:
                print "neue files vorhanden" 
                print newFiles
            self.fileSet = self.fileSet | newFiles
            message = ("refFL", self.fileSet)
            self.outQueue.put(message, True)
            #print "tolll"
            #print self.folderName
            time.sleep(self.mainLoopTimeout)
            n +=1
        
    def overlayWait(self):
        while(True):
            currentCommand = self.inQueue.get(True)
            print "message received"
            if currentCommand[0] == "refFL":
                newFiles = currentCommand[1] - self.fileSet
                
            elif currentCommand[0] == "reqFile":
                reply = ""
                self.outQueue.put(reply, True)
                pass
            elif currentCommand[0] == "":
                pass
            else:
                print "Application ERROR: received unknown message from Overlay "
        
    def vergleichListen(self, otherList):
        pass
    
    def cutFileIntoPieces(self):
        pass
        
a = Application()