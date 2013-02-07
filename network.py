import socket
from threading import Thread
import time
import sys
import Queue
import random
import zlib
import hashlib
import re
from datetime import datetime

class Network(object): 
	def __init__(self, ip, pRecv, startPort, countPort): 
		self.__ip = ip
		self.__portRecv = pRecv
		self.__portQueue = Queue.Queue()
		for i in range(countPort): 
			self.__portQueue.put(startPort + i)
		self.__sendQueue = Queue.Queue()
		for i in range(10): 
			self.__sendQueue.put(i)
		self.__threadArray = []
 
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
	#			print "fileTransfer"
				sendQueue.put(("fileTransfer", "127.0.0.1", portSend, "files/filetrans"))
	#			return
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
	#	print "recvTCP start ", port
		hatshi = ""
		try:
			sockRecv = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
			sockRecv.bind(("", port)) 
			sockRecv.settimeout(1)
			sockRecv.listen(1)
		except socket.error as msg:
			sockRecv = None
		try:
			index = 1
			while True: 
	#			print "warte auf TCP1", str(port)
				try:
					con, addr = sockRecv.accept()
				except socket.timeout:
	#				print "Timeout %d abgelaufen %d" % (index, port)
					if eingabe == "ende":
						break
					if index == 10:
						print "Daten wurden nicht empfangen die ERSTE %d" % port
						self.__portQueue.put(port)
						#nachricht an appli das daten nicht gesendet wurden						
						return
					index = index + 1
					continue
		#		print "warte auf TCP2"
				index = 0
				while True:
					try:
		#				print "warte auf gegenstelle"
						antwort = con.recv(1024)
		#				print "antwort bekommen"
						break
					except socket.timeout:
						if index == 10:
							print "Daten wurden nicht empfangen die ZWEITE %d" % port
							self.__portQueue.put(port)
							#nachricht an appli das daten nicht gesendet wurden						
							return
						index = index + 1
						if eingabe == "ende":
							break
				(stat, filo, hatshi) = re.split(r";", antwort)
		#		print "%s mit %s und Hash %s" % (stat, filo, hatshi)
				if stat == "LETSGOON":
					con.send("LETSGOON")
		#			print "send LETSGOON"
					recvData = ""
					while True:
						start = datetime.now().microsecond
						data = con.recv(BUFFERSIZE_FILE)
						if not data:
							break
						recvData = recvData + data
						ende = datetime.now().microsecond
						bitRate = float(len(data)*8) / float((ende - start))
						print "Transferate %0.3f Mbit/s" % bitRate
					filoName = "files/testfile" + str(time.clock())
					filo = open(filoName,"wb")
					filo.write(recvData)
					filo.close()
					self.__portQueue.put(port)
					break
		except socket.error as msg:
			#sockRecv.close()
			#sockRecv = None
			print msg
	#	print "[SEND] " + str(ip) + ":" + str(port) + " sendet " + nachricht
		try:
			sockRecv.close()
		except socket.error as msg:
			sockRecv = None
	#	print "recvTCP ende", port

	def __sendTCP(self, ip, port, filo):
	#	print "sendTCP start "
	#	print "%s:%s will %s" % (ip, port, filo)
		sockSend = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		sockSend.connect((ip, int(port)))
		hatshi = "hatshiiiiiiir"
		try: 
	#		while True: 
	#			nachricht = raw_input("Nachricht: ")
			nachricht = "LETSGOON;" +  filo + ";" + hatshi
	#		print "NACHRICHT: " + nachricht
			sockSend.send(nachricht) 
	#		print "NACHRICHT gesendet"
			index = 0
			while True:
				try:
					antwort = sockSend.recv(1024)
					break
				except socket.timeout:
					if index == 10:
						print "Daten wurden nicht empfangen die DRITTE %d" % port
						#self.__portQueue.put(port)
						#nachricht an appli das daten nicht gesendet wurden						
						return
					index = index + 1
					if eingabe == "ende":
						break
	#		print antwort
			if antwort == "LETSGOON":
	#			print "START file senden"
				try:
					sendFile = open(filo, 'rb')
				except:
					etype, evalue, etb = sys.exc_info()
					evalue = etype("Cannot open file: %s" % evalue)
					raise etype, evalue, etb
				while True:
					chunk = sendFile.read(BUFFERSIZE_FILE)
					if not chunk:
						break  # EOF
					sockSend.sendall(chunk)
		except socket.error as msg:
			sockSend.close()
			sockSend = None
			print msg
		finally: 
			sockSend.close()
	#	print "sendTCP ende"
        
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
					hatshi0 = self.__send(sendIP, sendPort, "OVERSTAT" + nachricht)
					while True:
	#					print "huhu"
						receipt = ""	
						try:
							hatshi1 = receiptQueue.get(True, 1.0)
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
						if hatshi0 == hatshi1:
	#						print "ABBRECHEN"
							break
				elif sendCase == "fileTransfer":
	#				print "UDPsend filetrans"
					sendPortTcp = self.__portQueue.get()
					threadTCP = Thread(target=self.__recvTCP, args=(sendPortTcp, "hallo welt"))
					self.__threadArray.append(threadTCP)
					threadTCP.start()
					self.__send(sendIP, sendPort, "FILETRAN" + str(sendPortTcp) + "," + nachricht)
	#				self.__recvTCP(sendPortTcp, "hallo welt")
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
				stat = nachricht[0:8]
				nachricht = nachricht[8:]
			except socket.timeout:
				if eingabe == "ende":
					break
			if not(daten == "") and (hatshi0 == hatshi1):
				if stat == "RECEBACK":
		#			print "Quittung erhalten"
					receiptQueue.put(nachricht)
				elif stat == "OVERSTAT":
					self.__send(senderIP, int(senderPort), "RECEBACK" + hatshi1)
		#			sendQueue.put(hashi + "True")
					print "[RECV] %s %s %s %s %s" % (addr[0], addr[1], senderIP, senderPort, nachricht)
				elif stat == "FILETRAN":
					(senderPort, nachricht) = re.split(r",", nachricht)
					threadTCP = Thread(target=self.__sendTCP, args=(senderIP, senderPort, nachricht))
					self.__threadArray.append(threadTCP)
					threadTCP.start()
		#			print "%s will an Port %s das File %s" % (senderIP, senderPort, nachricht)
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
startTcpPort = 60000
countTcpPort = 10
#sys.exit()

sendQueue = Queue.Queue()
receiptQueue = Queue.Queue()

eingabe = ""
HASHLENGTH = 5
BUFFERSIZE_UDP = 1024
BUFFERSIZE_TCP = 1024
BUFFERSIZE_FILE = 65536

network = Network(ip, portRecv, startTcpPort, countTcpPort)
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
    
