import os

partSize = 1024

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

def getFilePart(partNumb, file):
    fileSize = os.path.getsize(file)
    partCount = fileSize // partSize
    partLenLast = fileSize % (partSize)
    
    if partLenLast > 0:
        partCount = partCount + 1
        
    if partNumb > partCount:
        print "partNumb zu gross"
        return
    elif partNumb < 1:
        print "partNumb muss positiv sein"
    
    fo = open(file, "rb")
    posFrom = partSize * (partNumb - 1)
    fo.seek(posFrom, 0);
    str = fo.read(partSize);
    fo.close()
    return str


print getFilePart(4, "files/filetrans")
print getFileSize("files/filetrans")
print getPartLenLast("files/filetrans")
print getPartCount("files/filetrans")

