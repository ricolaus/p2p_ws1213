import socket
import threading
import time
import sys
import Queue
import random
import zlib
import hashlib

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
            
    
	def __test1(self):
		print "test1 start"
		while True:
			#print "Hallo"
			zahl = random.randint(0, 100000000)
			sendQueue.put(str(zahl))
			time.sleep(random.uniform(0.1,3.0))
			if eingabe == "ende":
				break
		print "test1 ende"        
    
	def __test2(self):
		print "test2 start"
		print "test2 ende"

	def __send(self, ip, port, nachricht):
		try:
			sockSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		except socket.error as msg:
			sockSend = None
		try:
			sockSend.sendto(nachricht, (ip, port))
		except socket.error as msg:
			sockSend.close()
			sockSend = None
		print "[SEND] " + str(ip) + ":" + str(port) + " sendet eine " + nachricht
		try:
			sockSend.close()
		except socket.error as msg:
			sockSend = None
        
	def __sendUdp(self):
		print "sendUdp start"
		
		while True:
			#print "Hallo"
			try:
				nachricht = sendQueue.get(True, 1.0)
				nachricht = str(hashlib.md5(nachricht).hexdigest())[:HASHLENGTH] + nachricht
				self.__send(self.__ip, self.__port, nachricht)
			except Queue.Empty:
				if eingabe == "ende":
					break
			#print "sendUdp" + nachricht
	#		while True:
	#			print "huhu"
	#			receipt = ""	
	#			try:
	#				receipt = receiptQueue.get(True, 1.0)
	#			except Queue.Empty:
	#				if eingabe == "ende":
	#					break
	#			if receipt == True:
	#				break
			#time.sleep(0.1)
		print "sendUdp ende"
    
	def __recvUdp(self):
		print "recvUdp start"
		sockRecv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sockRecv.bind((self.__ip, self.__port))
		sockRecv.settimeout(1.0)
		while True:
			if eingabe == "ende":
				break
			daten = ""
			addr = ""
			try:
				daten, addr = sockRecv.recvfrom(BUFFERSIZE)
			except socket.timeout:
				if eingabe == "ende":
					break
			if not(daten == ""):
	#			if daten[:HASHLENGTH] == "True":
	#				print "Quittung erhalten"
	#				receiptQueue.put((True,daten[0:HASHLENGTH])
	#			else:
					nachricht = daten[HASHLENGTH:]
					hashi = hashlib.md5(nachricht).hexdigest()[:HASHLENGTH]
					if str(hashi) == daten[0:HASHLENGTH]:
						hashTest = True
	#					sendQueue.put(hashi + "True")
					else:
						hashTest = False
	#					sendQueue.put(hashi + "False")
					print "[RECV] %s %s %s %s" % (addr[0], addr[1], hashTest, nachricht)
			#time.sleep(0.1)
		sockRecv.close()
		print "recvUdp ende"
 


#for eachArg in sys.argv:   
#	print eachArg
if len(sys.argv) < 5:
	print 'Prgramm wie folgt starten:'
	print 'Modus: 1 --> "Daten senden" 2 --> "keine Daten senden"'
	print 'python network.py [IP] [PortSend] [PortRecv] [Modus]'
	sys.exit()
ip = sys.argv[1]
portRecv = int(sys.argv[2])
portSend = int(sys.argv[3])
#sys.exit()

sendQueue = Queue.Queue()
receiptQueue = Queue.Queue()

eingabe = ""
HASHLENGTH = 5
BUFFERSIZE = 1024

meine_threads = []
threadRecv = UdpThread("recv", ip, portRecv)
meine_threads.append(threadRecv) 
threadRecv.start()
threadSend = UdpThread("send", ip, portSend) 
meine_threads.append(threadSend) 
threadSend.start()
if int(sys.argv[4]) == 1:
	threadTest1 = UdpThread("test1", "", portSend) 
	meine_threads.append(threadTest1) 
	threadTest1.start()


#time.sleep(1.0)

while 1:
    eingabe = raw_input("> ") 
    if eingabe == "ende": 
        break
 
    
sys.exit(-1)
#for t in meine_threads: 
#    t.join()
    
