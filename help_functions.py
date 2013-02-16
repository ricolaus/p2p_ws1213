import os
import pygtk
import gtk

class MyProgram:

    def __init__(self):

        # create a new window

        app_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        app_window.set_size_request(1920, 1080)
        app_window.set_border_width(10)
        app_window.set_title("MyProgram title")
        app_window.connect("delete_event", lambda w,e: gtk.main_quit())

        # Program goes here  ...

        app_window.show()

        return

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    MyProgram()
    main()

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

def readFilePart(partNumb, file):
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

def writeFilePart(partNumb, file):
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


#writeFilePart (4, "files/filetrans")
#print readFilePart(4, "files/filetrans")
#print getFileSize("files/filetrans")
#print getPartLenLast("files/filetrans")
#print getPartCount("files/filetrans")

