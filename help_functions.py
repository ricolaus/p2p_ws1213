import os
import pygtk
import gtk

class Gui:

    def __init__(self):

        # Create an Image object for a PNG file.
        file_name = "800px-Png-logo.png"
        pixbuf = gtk.gdk.pixbuf_new_from_file(file_name)
        pixmap, mask = pixbuf.render_pixmap_and_mask()
        image = gtk.Image()
        image.set_from_pixmap(pixmap, mask)

        # Create a window.
        window = gtk.Window()
        window.set_title("PNG file")
        window.connect("destroy", gtk.main_quit)

        # Show the PNG file in the window.
        window.add(image)
        window.show_all()

if __name__ == "__main__":
    Gui()
    gtk.main()

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

