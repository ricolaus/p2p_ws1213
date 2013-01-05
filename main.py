import sys
import Queue
#import copy

class Queue(object):
    def __init__(self):
        self.list = [] # or: self.list = list()

    def append(self, objekt):
        self.list.append(objekt) 

    def pop(self):
        if len(self.list) > 0:
            objekt = self.list.pop(0)
            return objekt
        else:
            return None

##    def output(self):
##        return self.list


inQueue = Queue()
outQueue = Queue()
