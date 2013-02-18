import threading
import time
import os
import hashlib
from os.path import isfile, join
import re
import shutil
import random
import help_functions
   
class Application:
    def __init__(self, path = "/User1/", q1 = None, q2 = None, q3=None):
        self.folderName = path
        self.mainLoopTimeout = 3
        self.fileSet = {}
        # dict: (fileName , fileHash) : (partsList, maxParts, 0, "0")
        self.partSize = help_functions.partSize
        self.maxReqNumber = 5
        self.maxSendNumber = 5
        self.fileSetLock = threading.Lock()
        
        self.reqFiles = {}
        #dict of requested parts format: (filename, filehash, part) : ownerName
        #should contain at any time every ownerName at most once
        self.sendFiles = {}
        #dict of currently send parts format_: (filename, filehash, part) : receiverName
        #should contain at any time every receiverName at most once
        self.filesToComplete = set()
        #set of files that will soon be a complete files and Parts Folder deleted
        #do not send any part of this files to anyone
        self.inQueue = q1
        #queue from  overlay       
        self.outQueue = q2 
        #queue to overlay    
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
            # TODO: need a lock here, so no lookup for file, if currently a file is written
            self.fileSetLock.acquire()
            self.fileSet = self.currentDirFiles()
            
            self.fileSet.update( self.incompletFileDir() )
            #print self.fileSet
            message = ("refFL", self.fileSet)
            #message = ("refFL", right)
            self.outQueue.put(message, True)
            self.fileSetLock.release()
            #print "tolll"
            #print self.folderName
            time.sleep(self.mainLoopTimeout)

        
    def overlayWait(self):
        while(True):
            currentCommand = self.inQueue.get(True)
            self.fileSetLock.acquire()
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
            self.fileSetLock.release()
             
    def processIncFileTransSend(self, message):
        #target Username is also identifier
        targetUsername, filePath, stat = message
        #find entry in sendFiles by Username, there should be only one entry with value == UserName
        for key, value in self.sendFiles.items():
            if value == targetUsername:
                del self.sendFiles[key]
                if (key[0], key[1]) in self.filesToComplete and self.noPartisSend(key[0], key[1]):
                    self.createFileFromParts(key[0], key[1])
                    self.filesToComplete.remove(key)
                break
        # TODO: if file in filestocomplete check if still in send.Files, else create files from parts
        
    
    def processIncFileTransRec(self, message):
        fileName, fileHash, partNumber, stat = message
        if stat: 
            #create fileSet entry if first part received
            if (fileName, fileHash) not in self.fileSet:
                infoFile = open(join(self.folderName + r"."+fileName+r"_"+fileHash, r".info"), 'r')
                maxParts = infoFile.read()
                infoFile.close()
                self.fileSet[fileName, fileHash] = ([str(partNumber)], maxParts, 0, "0")
            #add PartNumber to parts-list in fileSet-entry
            else:
                
                x = set(self.fileSet[(fileName, fileHash)][0])
                x.add(str(partNumber))
                del self.fileSet[(fileName, fileHash)][0][:]
                self.fileSet[(fileName, fileHash)][0].extend(list(x))
                print self.fileSet[(fileName, fileHash)][0]
            #if all file parts received, create complete file or finish first sending parts
            if self.allPartsReceived(fileName, fileHash):
                if self.noPartisSend(fileName, fileHash):
                    self.createFileFromParts(fileName, fileHash)
                else:
                    self.filesToComplete.add((fileName, fileHash))
        #delete reqFiles entry
        #print self.reqFiles
        del self.reqFiles[fileName, fileHash, str(partNumber)]
        
    
    def processIncReqFile(self, message):
        fileName, fileHash, part, senderUsername, port = message
        #part = "0"
        # TODO: decide to send the file or not, policy, maybe test if part is really in fs
        if (fileName, fileHash) not in self.filesToComplete and (fileName, fileHash) in self.fileSet and not self.alreadySendingToReceiver(senderUsername) and (fileName, fileHash, part) not in self.sendFiles and self.maxSendNumber > len(self.sendFiles):
            # TODO: problem if filename is a version-filename, so real-file-name and filetablename is different from 
            fsName = createFSname(fileName, self.fileSet[(fileName, fileHash)][3])
            #parts list is not empty -> parts in special dir
            if len(self.fileSet[(fileName, fileHash)][0]) != 0:
                filepath = self.getAbsPartPath(fileName, fileHash, part)
                part = "0"
            #full file existing
            else:
                filepath = join(self.folderName, fsName)
                
            # TODO: wird uebergeben nicht auf 0 festgelegt
            self.sendFiles[(fileName, fileHash, part)] = senderUsername
            reply = ("sendFile", filepath,  part, senderUsername, port)
            self.outQueue.put(reply, True)
            
        
    
    def processIncRefFl(self, message):
        recFiles, sendUser, urgent = message
        print recFiles
        newFiles = self.compareFileLists(recFiles)
        print newFiles
        #print newFiles
        #message urgent? -> send refFl
        if urgent:
            self.outQueue.put(("refFL", self.fileSet), True)
            
        # TODO: new function that chooses which file to request
        
        if len(newFiles) > 0:
            
            fname, fhash, part = self.choosePart(newFiles)
            #for fname, fhash in newFiles.iterkeys():
                #TODO: Parts: policy which to take
                #part = "0"
                
            if (fname, fhash, part) not in self.reqFiles and self.maxReqNumber > len(self.reqFiles) and not self.alreadyReceivingFromSender(sendUser) :
                # TODO: reqFile-message needs parts requested
                self.reqFiles[(fname, fhash, str(part))] = sendUser
                self.createpartsFolder(fname, fhash, newFiles[fname,fhash][1])
                reply = ("reqFile", fname, fhash, part, sendUser)
                self.outQueue.put(reply, True)
                #break
    
    def choosePart(self, newList):
        
        fileName, fileHash = random.choice(newList.keys())
        #print fileName
        #print fileHash
        #print newList[(fileName, fileHash)][0]
        part = random.choice(newList[(fileName, fileHash)][0])
        return fileName, fileHash, part
    
    #compare received Filelist and reqFiles with received filelist, return newfiles dic
    def compareFileLists(self, otherList):
        newList = {}
        for entry in otherList:
            if entry not in self.fileSet:
                newList[entry] = otherList[entry]
                #complete file, so all parts must be added to partsList
                if newList[entry][0] == []:
                    for i in range(1 , int(otherList[entry][1])+1):
                            newList[entry][0].append(str(i)) 
            else:
                #only incomplete file in folder
                if self.fileSet[entry][0] != []:
                    #if file was complete write every part in the partsList
                    
                    #create entry in newList
                    newList[entry] = ([], otherList[entry][1], otherList[entry][2], otherList[entry][3])
                    if otherList[entry][0] == []:
                        #create list was all part numbers
                        for i in range(1 , int(otherList[entry][1])+1):
                            if str(i) not in self.fileSet[entry][0]: 
                                newList[entry][0].append(str(i)) 
                            
                        #take all unknown parts
                    else:
                        for part in otherList[entry][0]:
                            if part not in self.fileSet[entry][0]:
                                newList[entry][0].append(part)
                    #delete entry, if there was not any new part
                    if newList[entry][0] == []:
                        del newList[entry]
                    
        #delete all entries that are already requested
        for reqFile, reqHash, reqPart in self.reqFiles:
            if (reqFile, reqHash) in newList.keys():
                if reqPart in newList[reqFile, reqHash][0]:
                    pos = newList[reqFile, reqHash][0].index(reqPart)
                    del newList[reqFile, reqHash][0][pos]
            #delete komplete entry if part list is empty
                if newList[reqFile, reqHash][0] == []:
                    del newList[reqFile, reqHash] 
                        
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
                size = help_functions.getPartCount(join(self.folderName, fname))
                time = os.path.getmtime(join(self.folderName, fname))
                filelist[(flistname, fhash)] = ([], str(size), time, version )
            
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
    
    def allPartsReceived(self, fileName, fileHash):
        try:
            if len(set(self.fileSet[(fileName, fileHash)][0])) == int(self.fileSet[(fileName, fileHash)][1]):
                if len(self.fileSet[(fileName, fileHash)][0]) != len(set(self.fileSet[(fileName, fileHash)][0])):
                    print "ERRRRRRRRRRRRRRRRRRRRRRRRRRRRRROR" , self.fileSet[(fileName, fileHash)][0]
                return True
            else:
                return False
        except Exception:
            print "BBBBBBBBBBBBBBBBBBBGGGGGGGGGGG EXCEPTION"
            print self.fileSet[(fileName, fileHash)][0]
            print self.fileSet[(fileName, fileHash)][1]
            os.abort()
        
    def createFileFromParts(self, fileName, fileHash):
        
        if self.allPartsReceived(fileName, fileHash):
            vers = self.nextVersion(fileName, fileHash)
            fsName = createFSname(fileName, vers)
            filePath = join(self.folderName, fsName)
            mfile = open(filePath, "w+b")
            #real range needed
            for i in range(1, int(self.fileSet[fileName,fileHash][1]) + 1):
                partPath = self.getAbsPartPath(fileName, fileHash, str(i))
                partFile = open(partPath,"rb")
                mfile.write(partFile.read())
                partFile.close()
                
            mfile.close()
            partFolder = join(self.folderName, r"." + fileName + r"_" + fileHash)
            shutil.rmtree(partFolder)
            #delete all parts in the parts-list
            del self.fileSet[(fileName, fileHash)][0][:] 
     
    def nextVersion(self, fileName, fileHash):
        versions = []
        for i in self.fileSet:
            if i[0] == fileName and i[1] != fileHash:
                versions.append(int (self.fileSet[i][3]))
        
        if len(versions) == 0:
            return "0"
        else:
            return str( int(max(versions)) + 1 )
        # TODO: evtl. noch reqSet anschauen damit nicht gleichzeitig eine naechste versionsnummer gewaehlt wird, oder lock auf fkt.
        
    
    def alreadySendingToReceiver(self, receiver):
        if receiver in self.sendFiles.values():
            return True
        else:
            return False
    
    def alreadyReceivingFromSender(self, sender):
        if sender in self.reqFiles.values():
            return True
        else:
            return False
        
    #returns directory of existing incomplete files (parts folder) formatet like self.fileSet  
    def incompletFileDir(self):
        dirList = {}
        

        x = re.compile(r"\.(.+)_([0-9a-f]{32})$")  
        pathes = os.listdir(self.folderName)  
        for path in pathes:
            partsList = []
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

        return dirList
    
    
    def noPartisSend(self, fileName, fileHash):
        for entry in self.sendFiles:
            if entry[0] == fileName and entry[1] == fileHash:
                return False
        return True
    
    
    
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
    while True:
        try:
            md5 = hashlib.md5()
            f = open(filepath,'rb')
            while True:
                data = f.read(8192)
                if not data:
                    break
                md5.update(data)
            return md5.hexdigest()
        except Exception:
            continue
    
    

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


#x = ([],"2")
#print x
#x[0].append(1)
#print x
#a = Application()
#print a.incompletFileDir()