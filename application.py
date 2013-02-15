import threading
import time
import os
import hashlib
from random import random
from os.path import isfile, join
import re
import ast

    
class Application:
    def __init__(self, path = "/home/imon/Uni-11/P2P/Test", q1 = None, q2 = None, q3=None):
        self.folderName = path
        self.mainLoopTimeout = 3
        self.fileSet = {}
        self.partSize = 8192
        self.maxReqNumber = 5
        self.maxSendNumber = 5
        #liste der angefragten parts
        self.reqFiles = []
        self.sendFiles = []
        #queue from and to overlay
        self.inQueue = q1       
        self.outQueue = q2 
        #queue for user input, maybe not needed
        self.interfacequeue = q3 
        self.mainLoopThread = threading.Thread(target=self.mainLoop)
        self.mainLoopThread.start()
        self.overlayWaitThread = threading.Thread(target=self.overlayWait)
        self.overlayWaitThread.start()
        #self.mainLoopThread.join()
       
    def mainLoop(self):
        while(True):
            # TODO: better/more efficient comparison of oldFileset and currentFileset, parts?
            fss = str(self.currentDirFiles())
            right = ast.literal_eval(fss)
            #self.fileSet = self.currentDirFiles()
            #message = ("refFL", self.fileSet)
            message = ("refFL", right)
            self.outQueue.put(message, True)
            #print "tolll"
            #print self.folderName
            time.sleep(self.mainLoopTimeout)

        
    def overlayWait(self):
        while(True):
            currentCommand = self.inQueue.get(True)
            # print "message received"
            if currentCommand[0] == "refFL":
                self.processIncRefFl(currentCommand)
                
            elif currentCommand[0] == "reqFile":
                self.processIncReqFile(currentCommand)
            # TODO: receive message from network    
            else:
                print "Application ERROR: received unknown message from Overlay "
    
    def processIncReqFile(self, message):
        msgType, fileName, fileHash, senderUsername, port = message
        
        # TODO: decide to send the file or not
        #maybe add:      and not alreadySendingToReceiver(senderUsername) 
        if (fileName, fileHash) in self.fileSet and (fileName, fileHash, senderUsername) not in self.sendFiles and self.maxSendNumber > len(self.sendFiles):
            # TODO: problem if filename is a version-filename, so real-file-name and filetablename is different from 
            fsName = createFSname(fileName, self.fileSet[(fileName, fileHash)][3])
            filepath = join(self.folderName, fsName)
            self.sendFiles.append((fileName, fileHash, senderUsername))
            reply = ("sendFile", filepath, senderUsername, port, 0)
            self.outQueue.put(reply, True)
            
        
    
    def processIncRefFl(self, message):
        msgType, recFiles, sendUser, urgent = message
        newFiles = self.compareFileLists(recFiles)
        #message urgent? -> send refFl
        if urgent:
            self.outQueue.put(("refFL", self.fileSet), True)
            
        # TODO: new function that chooses which file to request
        if len(newFiles) > 0:
            for fname, fhash in newFiles.iterkeys():
                #TODO: Parts
                if (fname, fhash, sendUser) not in self.reqFiles and self.maxReqNumber > len(self.reqFiles) :
                    #
                    reply = ("reqFile", fname, fhash, sendUser)
                    self.reqFiles.append((fname, fhash, sendUser)) 
                    self.outQueue.put(reply, True)
    
    
    #compare received Filelist and return List of new files    
    def compareFileLists(self, otherList):
        # TODO: lock auf filelist notwendig, damit sie waehrend des vergleichs nicht veraendert wird
        newList = {}
        for entry in otherList:
            if entry not in self.fileSet:
                newList[entry] = otherList[entry]
            else:
                # TODO: zusaetzlich betrachten ob partlist stuecke enthaelt
                pass               
        return newList
    
    #liste der 
    def currentDirFiles(self):
        files = os.listdir(self.folderName)
        filelist = {}
        for fname in files:
            #only files are accepted
            if isfile(join(self.folderName, fname)):
                #erstmal zeitstempel betrachten
                #ueberpruefen ob versionierung vorhanden
                flistname, version = getFileVersion(fname)
                #if version != "0":
                #    print flistname + "\t" + fname +"\t" + version        
                fhash = getHash(join(self.folderName, fname))
                size = os.path.getsize(join(self.folderName, fname))
                time = os.path.getmtime(join(self.folderName, fname))
                filelist[(flistname, fhash)] = ([], size, time, version )
            
            #onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
        return filelist

    def createpartsFolder(self, filename, fhash):

        dirName = r"." + filename + r"_" + fhash
        dirPath = join(self.folderName, dirName)
        if not os.path.isdir(dirPath):
            os.mkdir(dirPath)
     
    def nextVersion(self, filename, fhash):
        versions = []
        for i in self.fileSet:
            if i == filename:
                versions.append(self.fileSet[i][3])
        return int(max(versions)) + 1
        # TODO: evtl. noch reqSet anschauen damit nicht gleichzeitig eine naechste versionsnummer gewaehlt wird, oder lock auf fkt.
        pass
    
    def alreadySendingToReceiver(self, receiver):
        for it in self.reqFiles:
            if it[2] == receiver:
                return True
        
        return False
        
#    #lookup files in the shared directory and change fileset accordingly
#    #(name, hash, [partlist], insgesamte anz parts)
#    def lookupDirFiles(self):
#        
#        filelist = self.currentDirFiles()
#        
#        for entry in self.fileSet.keys():
#            if entry in filelist:
#                #eintrag schon in der tabelle vorhanden
#                del filelist[entry]
#                pass
#            else:
#                #eintrag nicht mehr vorhanden
#                del self.fileSet[entry]
#        
#        files = os.listdir(self.folderName)
#        newFileList = []
#        for fil in self.fileSet():
#            #falls nicht in fileset, kompletten eintrag erzeugen
#            #falls bereits in fileset: 1.timestamp vergleichen, wenn gleich nix aendern, falls anders allten eintrag loeschen/auf aktuellem anpassen
#            #falls eintrag in fileset, aber nicht im directory eintrag aus fileset loeschen
#            if not fil in files:
#                #fil nicht mehr im shareddirectory, also loeschen
#                self.fileSet.remove(fil)
#                self.files.remove(fil)
#                pass
#            if fil in files:
#                #look for timestamp
#                pass
#            if False:
#                #create entry for new file 
#                name = fil
#                fhash = getHash(fil)
#                partnumbers = 70011/ self.partSize
#                newFileList.append((name, fhash, [], partnumbers))
        
def getHash(filepath): 
    md5 = hashlib.md5()
    f = open(filepath,'rb')
    while True:
        data = f.read(8192)
        if not data:
            break
        md5.update(data)
    return md5.hexdigest()
    
    

def getFileVersion( filename):
    #filename = "ganzGrossgz(copy20)"
    p = re.compile(r"(.+)\(copy([1-9]+\d*)\)\.([^.]+)$")
    r = re.compile(r"(.?[^.]*)\(copy([1-9]+\d*)\)$")
    a = r.match(filename)
    if a:
        return a.groups()
    b = p.match(filename)
    if b:
        name, vers,  extension = b.groups()
        return (name+"."+extension, vers)
    
    return (filename, "0")
        
            
def createFSname(filename, vers):
    if vers == "0":
        return filename
    
    p = re.compile(r"(.+)\.([^.]+)$")
    r = re.compile(r"(.?[^.]+)$")
    a = r.match(filename)
    if a:
        return filename +r"(copy" + vers + r")"
    b = p.match(filename)
    if b:
        name,  extension = b.groups()
        return name + vers + "." +extension
    # TODO: error message
    return None    
    
#a = getFileVersion("")
#print a.groups()
#a = Application()
#a.currentDirFiles()