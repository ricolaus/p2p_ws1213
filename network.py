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
			case = 0 #random.randint(0, 1)
			if case == 0:
				#print "Hallo"
				message = ""
				testRange = random.randint(35, 9000)
				for i in range(testRange): #35 bei 64 Byte
					message = message + str(random.randint(0, 9))
				sendQueue.put(("message", "127.0.0.1", portSend, message))
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
				(stat, filo, hatshi) = antwort.split(";", 2)
		#		print "%s mit %s und Hash %s" % (stat, filo, hatshi)
				if stat == "LETSGOON":
					con.send("LETSGOON")
		#			print "send LETSGOON"
					recvData = ""
					bitRate = 0
					bitRateCounter = 0
					while True:
						start = datetime.now().microsecond
						data = con.recv(BUFFERSIZE_FILE)
						if not data:
							break
						recvData = recvData + data
						ende = datetime.now().microsecond
						bitRate = bitRate + float(len(data)*8) / float((ende - start))
						bitRateCounter = bitRateCounter + 1
					print "Transferate %0.3f Mbit/s" % (bitRate / bitRateCounter)
					filoName = "files/testfile" + str(time.clock())
					filo = open(filoName,"wb")
					filo.write(recvData)
					filo.close()
					print datetime.now().microsecond
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

	def __send(self, ip, port, stat, nachricht):
		hatshi = ""
		partQueue = Queue.Queue()
	#	print len(nachricht)
		nachricht = stat + ";" + nachricht
		partSize = BUFFERSIZE_UDP - 33
		lenNachricht = len(nachricht)
		if lenNachricht > ((BUFFERSIZE_UDP - 33) * 255):
			print "Nachricht zu lang"
			return False
		partCount = lenNachricht // (partSize)
		partLenLast = lenNachricht % (partSize)
		if partLenLast == 0:
			partCount = partCount - 1
		print "partSize: %d partCount: %d partLenLast: %d errechnet: %d tatsaechlich: %d" % (partSize, partCount, partLenLast, (partCount * partSize + partLenLast), lenNachricht)
		for i in range(partCount):
			fromIndex = partSize * i
			toIndex = (partSize * i) + partSize
			partQueue.put((i + 1, partCount + 1, nachricht[fromIndex:toIndex]))
	#		print "%s von %d bis %d" % (nachricht[fromIndex:toIndex], fromIndex, toIndex)
		if partLenLast > 0:
			fromIndex = partSize * partCount
			toIndex = (partSize * partCount) + partLenLast
			partQueue.put((partCount + 1, partCount + 1, nachricht[fromIndex:toIndex]))
	#	print "%s von %d bis %d" % (nachricht[fromIndex:toIndex], fromIndex, toIndex)
		for i in range(partCount + 1):		
			try:
				sockSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				sendStat = False
				(part, partCount, partNachricht) = partQueue.get()
				partNachricht = str(hex(part)[2:4]) + ";" + str(hex(partCount)[2:4]) + ";" + self.__ip + ";" + str(self.__portRecv) + ";" + partNachricht
				hatshi0 = self.__calcHash(partNachricht)
				partNachricht = hatshi0 + ";" + partNachricht
				sockSend.sendto(partNachricht, (ip, port))
				print "[SEND0] " + str(ip) + ":" + str(port) + " sendet " + partNachricht
				if stat == "OVERSTAT":
	#				print "[HUHUHUHU]" + stat
					index = 1
					receStat = ""		
					while True:
						try:
							receStat, hatshi1 = receiptQueue.get(True, 1.0)
						except Queue.Empty:
							if index == 10:
								#Ansage nach oben das Host nicht erreichbar ist
								print "Host nicht erreichbar"
								break
							if eingabe == "ende":
								return
						if (receStat == "True") and (hatshi0 == hatshi1):
	#						print "ABBRECHEN"
							sendStat = True
							break
						else:
							sockSend.sendto(partNachricht, (ip, port))
							print "[SEND1] " + str(ip) + ":" + str(port) + " sendet " + partNachricht
							index = index + 1
				else:
					sendStat = True
	#				print "[SEND] " + str(ip) + ":" + str(port) + " sendet " + partNachricht
			except socket.error as msg:
				sockSend = None
			finally: 
				sockSend.close()
		return sendStat
        
	def __sendUdp(self):
		print "sendUdp start"
		while True:
			try:
				(sendCase, sendIP, sendPort, nachricht) = sendQueue.get(True, 1.0)
				if sendCase == "message":
					sendStat = self.__send(sendIP, sendPort, "OVERSTAT", nachricht)
					if sendStat == False:
						doNothing = True
	#					Ansage nach oben
				elif sendCase == "fileTransfer":
	#				print "UDPsend filetrans"
					sendPortTcp = self.__portQueue.get()
					threadTCP = Thread(target=self.__recvTCP, args=(sendPortTcp, "hallo welt"))
					self.__threadArray.append(threadTCP)
					threadTCP.start()
					self.__send(sendIP, sendPort, "FILETRAN", str(sendPortTcp) + "," + nachricht)
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
		recvDict = {}
		recvType = ""
		while True:
			try:
				daten, addr = sockRecv.recvfrom(BUFFERSIZE_UDP)
	#			print daten + " " + str(addr)
				(hashi1, daten) = daten.split(";", 1)
				hatshi0 = str(self.__calcHash(daten))
				(part, partCount, senderIP, senderPort, nachricht) = daten.split(";", 4)
				part = int(part, 16)
				partCount = int(partCount,16)
				recvDict[(part, partCount, senderIP, senderPort)] = nachricht
				if nachricht[:8] == "OVERSTAT":
					recvType = "OVERSTAT"
				if recvType == "OVERSTAT":				
					self.__send(senderIP, int(senderPort), "RECEBACK", "True;" + hashi1)
				if part == partCount:
					nachricht =  ""
					for i in range(partCount):
						nachricht = nachricht + recvDict[(i + 1, partCount, senderIP, senderPort)]
						del recvDict[(i + 1, partCount, senderIP, senderPort)]
	#				print "[NACHRICHT] " + nachricht
					self.__recvUdp2(nachricht, addr, senderIP, senderPort)
					recvType = ""
					continue
	#			print "%s %s %s %s %s %s" % (hashi1, part, partCount, senderIP, senderPort, nachricht)
			except socket.timeout:
				if eingabe == "ende":
					break
				continue
			#self.__recvUdp2(daten, addr)
		sockRecv.close()
		print "recvUdp ende"

	def __recvUdp2(self, nachricht, addr, senderIP, senderPort):
		(stat, nachricht) = nachricht.split(";", 1)
		print "[RECV] %s:%s nach %s %s %s" % (addr[0], addr[1], senderIP, senderPort, nachricht)
		if not(nachricht == ""):
			if stat == "RECEBACK":
				(stat, nachricht) = nachricht.split(";", 1)
				receiptQueue.put((stat, nachricht))
			elif stat == "OVERSTAT":
				#self.__send(senderIP, int(senderPort), "RECEBACK", "True;" + hatshi1)
				doNothing = True
	#			print "[DAS GEHT NACH OBEN] " + nachricht
			elif stat == "FILETRAN":
				(senderPort, nachricht) = nachricht.split(",", 1)
				threadTCP = Thread(target=self.__sendTCP, args=(senderIP, senderPort, nachricht))
				self.__threadArray.append(threadTCP)
				threadTCP.start()
		return True
 


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
BUFFERSIZE_UDP = 63
BUFFERSIZE_TCP = 1024
BUFFERSIZE_FILE = 65536

#test = hex(255)
#print "11 %d" % int(test[2:], 16)

#test = 10 // 3
#print test
#test = 10 % 3
#print test

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
    
