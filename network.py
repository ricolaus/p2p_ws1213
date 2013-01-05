import socket
import threading
import time
import sys
import Queue
import random

class UdpThread(threading.Thread): 
    def __init__(self, mode, ip, port): 
        threading.Thread.__init__(self)
        self.__mode = mode
        self.__ip = ip
        self.__port = port
 
    def run(self):
        if self.__mode == "send":
            self.__sendUdp()
        if self.__mode == "recv":
            self.__recvUdp()
        if self.__mode == "test1":
            self.__test1()
            
    
    def __test1(selfself):
        print "test1 start"
        while True:
            #print "Hallo"
            zahl = random.randint(0, 10)
            BriefkastenEinsZuZwei.put("Sende" + str(zahl))
            time.sleep(random.random())
            if eingabe == "ende":
                break
        print "test1 ende"        
    
    def __test2(selfself):
        print "test2 start"
        print "test2 ende"
        
    def __sendUdp(self):
        print "sendUdp start"
        sockSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            if not(BriefkastenEinsZuZwei.empty()):
                nachricht = BriefkastenEinsZuZwei.get()
                print "sendUdp" + nachricht
                sockSend.sendto(nachricht, (self.__ip, self.__port))
                print "sendUdp " + nachricht + " gesendet"
            time.sleep(0.1)
            if eingabe == "ende":
                break
        sockSend.close()
        print "sendUdp ende"
    
    def __recvUdp(self):
        print "recvUdp start"
        sockRecv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sockRecv.bind(("", self.__port))
            sockRecv.settimeout(1.0)
            while True:
                daten = ""
                addr = ""
                try:
                    daten, addr = sockRecv.recvfrom(1024)
                except socket.timeout:
                    if eingabe == "ende":
                        break
                if not(daten == ""):
                    print "[%s] %s" % (addr[0], daten)
                time.sleep(1.0)
        finally:
            sockRecv.close()
        print "recvUdp ende"
 

BriefkastenEinsZuZwei = Queue.Queue()
BriefkastenZweiZuEins = Queue.Queue()

eingabe = ""

meine_threads = []
threadRecv = UdpThread("recv", "", 50000)
meine_threads.append(threadRecv) 
threadRecv.start()
threadSend = UdpThread("send", "127.0.0.1", 50000) 
meine_threads.append(threadSend) 
threadSend.start()
threadTest1 = UdpThread("test1", "", 0) 
meine_threads.append(threadTest1) 
threadTest1.start()


time.sleep(1.0)

while 1:
    eingabe = raw_input("> ") 
    if eingabe == "ende": 
        break
 
    
sys.exit(-1)
#for t in meine_threads: 
#    t.join()
    