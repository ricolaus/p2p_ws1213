import threading
import time
import os
import hashlib
from os.path import isfile, join
import re

partSize = 1024
   
class Application:
    def __init__(self, path = "/User1/", q1 = None, q2 = None, q3=None):
        self.folderName = path
        self.mainLoopTimeout = 3
        self.fileSet = {}
        self.partSize = 8192
        self.maxReqNumber = 5
        self.maxSendNumber = 5
        #liste der angefragten parts
        self.reqFiles = {}
        self.sendFiles = {}
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
            #fss = str(self.currentDirFiles())
            #right = ast.literal_eval(fss)
            self.fileSet = self.currentDirFiles()
            
            self.fileSet.update( self.incompletFileDir() )
            message = ("refFL", self.fileSet)
            #message = ("refFL", right)
            self.outQueue.put(message, True)
            #print "tolll"
            #print self.folderName
            time.sleep(self.mainLoopTimeout)

        
    def overlayWait(self):
        while(True):
            currentCommand = self.inQueue.get(True)
            # print "message received"
            if currentCommand[0] == "refFL":
                self.processIncRefFl(currentCommand[1:])
                
            elif currentCommand[0] == "reqFile":
                self.processIncReqFile(currentCommand[1:])
            # TODO: receive message from network  
            elif currentCommand[0] == "fileTransRecv":
                self.processIncFileTransRec(currentCommand[1:])
            elif currentCommand[0] == "fileTransSend":
                self.processIncFileTransSend(currentCommand[1:])
                # "fileTransSend ", targetUsername, filePath, successflag)
            else:
                print "Application ERROR: received unknown message from Overlay "
                
    def processIncFileTransSend(self, message):
        #target Username is also identifier
        targetUsername, filePath, stat = message
        for key, value in self.sendFiles.items():
            if value == targetUsername:
                del self.sendFiles[key]
        
    
    def processIncFileTransRec(self, message):
        fileName, fileHash, partNumber, stat = message
        if stat:
            # TODO: if all parts received do not send more, until they are put together  (dont send and del), del folder
            #create fileSet entry if first part received
            if (fileName, fileHash) not in self.fileSet:
                infoFile = open(join(self.folderName + r"."+fileName+r"_"+fileHash, r".info"), 'r')
                maxParts = infoFile.read()
                infoFile.close()
                self.fileSet[fileName, fileHash] = ([str(partNumber)], maxParts, 0, "0")
            else:
                self.fileSet[(fileName, fileHash)][0].append(str(partNumber))
                
            
            #self.fileSet[(fileName, fileHash)][0].append(partNumber)
            
        del self.reqFiles[fileName, fileHash, str(partNumber)]
        
    
    def processIncReqFile(self, message):
        fileName, fileHash, part, senderUsername, port = message
        #part = "0"
        # TODO: decide to send the file or not, policy
        #maybe add:      and not alreadySendingToReceiver(senderUsername) 
        if (fileName, fileHash) in self.fileSet and not self.alreadySendingToReceiver(senderUsername) and (fileName, fileHash, part) not in self.sendFiles and self.maxSendNumber > len(self.sendFiles):
            # TODO: problem if filename is a version-filename, so real-file-name and filetablename is different from 
            fsName = createFSname(fileName, self.fileSet[(fileName, fileHash)][3])
            #parts list is not empty -> parts 
            if len(self.fileSet[(fileName, fileHash)][0]) != 0:
                filepath = self.getAbsPartPath(fileName, fileHash, part)
            #full file existing
            else:
                filepath = join(self.folderName, fsName)
            self.sendFiles[(fileName, fileHash, part)] = senderUsername
            reply = ("sendFile", filepath,  part, senderUsername, port)
            self.outQueue.put(reply, True)
            
        
    
    def processIncRefFl(self, message):
        recFiles, sendUser, urgent = message
        newFiles = self.compareFileLists(recFiles)
        #message urgent? -> send refFl
        if urgent:
            self.outQueue.put(("refFL", self.fileSet), True)
            
        # TODO: new function that chooses which file to request
        if len(newFiles) > 0:
            for fname, fhash in newFiles.iterkeys():
                #TODO: Parts: policy which to take
                part = "0"
                if (fname, fhash, part) not in self.reqFiles and self.maxReqNumber > len(self.reqFiles) and not self.alreadyReceivingFromSender(sendUser) :
                    # TODO: reqFile-message needs parts requested
                    self.reqFiles[(fname, fhash, part)] = sendUser
                    self.createpartsFolder(fname, fhash, newFiles[fname,fhash][1])
                    reply = ("reqFile", fname, fhash, part, sendUser)
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
                size = getPartCount(join(self.folderName, fname))
                time = os.path.getmtime(join(self.folderName, fname))
                filelist[(flistname, fhash)] = ([], size, time, version )
            
            #onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
        return filelist

    def createpartsFolder(self, filename, fhash, partNumber):

        dirName = r"." + filename + r"_" + fhash
        dirPath = join(self.folderName, dirName)
        if not os.path.isdir(dirPath):
            os.mkdir(dirPath)
            infoFile = open(join(dirPath, r".info"), 'w')
            infoFile.write(str(partNumber))
            infoFile.close()
     
    def nextVersion(self, filename, fhash):
        versions = []
        for i in self.fileSet:
            if i == filename:
                versions.append(self.fileSet[i][3])
        return int(max(versions)) + 1
        # TODO: evtl. noch reqSet anschauen damit nicht gleichzeitig eine naechste versionsnummer gewaehlt wird, oder lock auf fkt.
        
    
    def alreadySendingToReceiver(self, receiver):
        if receiver in self.reqFiles.viewvalues():
                return True
        else:
            return False
    
    def alreadyReceivingFromSender(self, sender):
        if sender in self.sendFiles.viewvalues():
                return True
        else:
            return False
        
    #returns directory of existing incomplete files (parts folder) formatet like self.fileSet  
    def incompletFileDir(self):
        dirList = {}
        partsList = []

        x = re.compile(r"\.(.+)_([0-9a-f]{32})$")  
        pathes = os.listdir(self.folderName)  
        for path in pathes:
            y = x.match(path)
            if y:
                dirPath = join(self.folderName, path)
                if os.path.isdir(dirPath):
                    for f in os.listdir(dirPath):
                        if f[:4] == "part":
                            partsList.append(f[4:])
                if len(partsList) > 0:
                    infoFile = open(join(dirPath, r".info"), 'r')
                    maxParts = infoFile.read()
                    infoFile.close()
                    dirList[y.group(1,2)] = (partsList, maxParts, 0, "0")
                    # dirList[y.group(1,2)] = ([], size, time, version )
        return dirList
    
    def getAbsPartPath(self,fileName, fileHash, part):
        absPath = join(self.folderName, r"." + fileName + r"_" + fileHash, "part" + part)
        return absPath
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

#x = re.compile(r"\.(.+)_([0-9a-f]{32})")    
#y = x.match(r".README_dc398ec03cf524964ecad3577deb4678")
#if y:
#    print y.groups()

def getFileSize(filePath):
    fileSize = os.path.getsize(filePath)
    return fileSize

def getPartLenLast(filePath):
    partLenLast = getFileSize(filePath) % (partSize)
    return partLenLast

def getPartCount(filePath):
    partCount = getFileSize(filePath) // partSize
    if getPartLenLast(filePath) > 0:
        partCount = partCount + 1
    return partCount

#a = Application()
#print a.incompletFileDir()