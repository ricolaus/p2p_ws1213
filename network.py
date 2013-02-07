import socket
from threading import Thread
import time
import sys
import Queue
import random
import zlib
import hashlib
import re

class Network(object): 
	def __init__(self, ip, pRecv): 
		self.__ip = ip
		self.__portRecv = pRecv
 
	def run(self):
		t0 = Thread(target=self.__recvUdp, args=())
		t0.start()
		t1 = Thread(target=self.__sendUdp, args=())
		t1.start()
		if mode == 1:
			t2 = Thread(target=self.__test1, args=())
			t2.start()
            
    
	def __test1(self):
		print "test1 start"
		while True:
			case = random.randint(0, 1)
			if case == 0:
				#print "Hallo"
				zahl = random.randint(0, 10)
				sendQueue.put(("message", "127.0.0.1", portSend, str(zahl)))
			else:
				print "filetransfer"
				sendQueue.put(("filetrans", "127.0.0.1", portSend, "filetrans"))
			time.sleep(random.uniform(0.1,3.0))
			if eingabe == "ende":
				break
		print "test1 ende"        
    
	def __test2(self):
		print "test2 start"
		print "test2 ende"

	def __send(self, ip, port, nachricht):
		hatshi = ""
		try:
			sockSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		except socket.error as msg:
			sockSend = None
		try:
			hatshi = self.__calcHash(nachricht)
			nachricht = hatshi + nachricht
			nachricht = self.__ip + ";" + str(self.__portRecv) + ";" + nachricht
			sockSend.sendto(nachricht, (ip, port))
		except socket.error as msg:
			sockSend.close()
			sockSend = None
		print "[SEND] " + str(ip) + ":" + str(port) + " sendet " + nachricht
		try:
			sockSend.close()
		except socket.error as msg:
			sockSend = None
		return hatshi

	def __recvTCP(self, port, data):
		hatshi = ""
		try:
			sockRecv = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
			sockRecv.bind(("", port)) 
			sockRecv.settimeout(2)
			sockRecv.listen(1)
		except socket.error as msg:
			sockRecv = None
			print msg
		try:
			while True: 
				print "warte auf TCP1"
				try:
					con, addr = sockRecv.accept()
				except socket.timeout:
					print "Timeout abgelaufen"
					if eingabe == "ende":
						break
					continue
				print "warte auf TCP2"
				while True: 
					data = con.recv(BUFFERSIZE_TCP)
					if not data: 
 						con.close() 
						break
					print "[%s] %s" % (addr[0], data) 
					#nachricht = raw_input("Antwort: ") 
					#con.send(nachricht)
				if eingabe == "ende":
					break
		except socket.error as msg:
			sockRecv.close()
			sockRecv = None
	#	print "[SEND] " + str(ip) + ":" + str(port) + " sendet " + nachricht
		try:
			sockRecv.close()
		except socket.error as msg:
			sockRecv = None
        
	def __sendUdp(self):
		print "sendUdp start"
		
		while True:
	#		print "Hallo"
	#		if eingabe == "ende":
	#			break
			index = 1
			hatshi0 = ""
			hatshi1 = ""
			try:
				(sendCase, sendIP, sendPort, nachricht) = sendQueue.get(True, 1.0)
				if sendCase == "message":
					hatshi0 = self.__send(sendIP, sendPort, nachricht)
					while True:
	#					print "huhu"
						receipt = ""	
						try:
							receipt = receiptQueue.get(True, 1.0)
							hatshi1 = receipt[0:HASHLENGTH]
							receipt = receipt[HASHLENGTH:]
	#						print receipt
						except Queue.Empty:
							if index == 10:
								#Ansage nach oben das Host nicht erreichbar ist
								print "Host nicht erreichbar"
								break
							if eingabe == "ende":
								return
							self.__send(sendIP, sendPort, nachricht)
							index = index + 1
						if receipt == "True" and hatshi0 == hatshi1:
	#						print "ABBRECHEN"
							break
				else:
					print "UDPsend filetrans"
					self.__recvTCP(60000, "hallo welt")
			except Queue.Empty:
				if eingabe == "ende":
					break
		print "sendUdp ende"

	def __calcHash(self, text):
		hatshi = hashlib.md5(text).hexdigest()[:HASHLENGTH]
		return hatshi
    
	def __recvUdp(self):
		print "recvUdp start"
		sockRecv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sockRecv.bind((self.__ip, self.__portRecv))
		sockRecv.settimeout(1.0)
		while True:
			if eingabe == "ende":
				break
			daten = ""
			addr = ""
			try:
				daten, addr = sockRecv.recvfrom(BUFFERSIZE_UDP)
				(senderIP, senderPort, daten) = re.split(r";", daten)
				nachricht = daten[HASHLENGTH:]
				hatshi0 = str(self.__calcHash(nachricht))
				hatshi1 = daten[0:HASHLENGTH]
			except socket.timeout:
				if eingabe == "ende":
					break
			if not(daten == ""):
				if nachricht[HASHLENGTH:] == "True":
		#			print "Quittung erhalten"
					receiptQueue.put(nachricht)
				else:
					if hatshi0 == hatshi1:
						hashTest = True
						self.__send(senderIP, int(senderPort), hatshi1 + "True")
		#				sendQueue.put(hashi + "True")
					else:
						hashTest = False
		#				sendQueue.put(hashi + "False")
					print "[RECV] %s %s %s %s %s %s" % (addr[0], addr[1], senderIP, senderPort, hashTest, nachricht)
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
mode = int(sys.argv[4])
#sys.exit()

sendQueue = Queue.Queue()
receiptQueue = Queue.Queue()

eingabe = ""
HASHLENGTH = 5
BUFFERSIZE_UDP = 1024
BUFFERSIZE_TCP = 1024

network = Network(ip, portRecv)
network.run()

#meine_threads = []
#threadRecv = UdpThread("recv", ip, portRecv)
#meine_threads.append(threadRecv) 
#threadRecv.start()
#threadSend = UdpThread("send", ip, portSend) 
#meine_threads.append(threadSend) 
#threadSend.start()
#if int(sys.argv[4]) == 1:
#	threadTest1 = UdpThread("test1", "", portSend) 
#	meine_threads.append(threadTest1) 
#	threadTest1.start()


#time.sleep(1.0)

while 1:
    eingabe = raw_input("> ") 
    if eingabe == "ende": 
        break
 
    
sys.exit(-1)
#for t in meine_threads: 
#    t.join()
    
