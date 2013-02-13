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
	def __init__(self, ip, pRecv, startPort, countPort, recvQueue, sendQueue): 
		self.__ip = ip
		self.__recvQueue = recvQueue
		self.__sendQueue = sendQueue
		self.__portRecv = pRecv
		self.__portQueue = Queue.Queue()
		for i in range(countPort): 
			self.__portQueue.put(startPort + i)
		self.__threadArray = []
		self.__HASHLENGTH = 5
		self.__BUFFERSIZE_UDP = 63
		self.__BUFFERSIZE_TCP = 1024
		self.__BUFFERSIZE_FILE = 65536
 
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
				message = ""
				testRange = random.randint(1, 50)
				for i in range(testRange): #35 bei 64 Byte
					message = message + str(random.randint(0, 9))
				self.__sendQueue.put(("message", "127.0.0.1", portSend, message))
			else:
				self.__sendQueue.put(("fileTransfer", "127.0.0.1", portSend, "files/filetrans"))
			time.sleep(random.uniform(0.1,3.0))
			if eingabe == "ende":
				break
		print "test1 ende"        
    
	def __test2(self):
		print "test2 start"
		print "test2 ende"

	def __recvTCP(self, port, filePath, fileHash):
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
				try:
					con, addr = sockRecv.accept()
				except socket.timeout:
					if eingabe == "ende":
						break
					if index == 10:
						print "Daten wurden nicht empfangen die ERSTE %d" % port
						self.__portQueue.put(port)				
						return
					index = index + 1
					continue
				index = 0
				while True:
					try:
						antwort = con.recv(1024)
						break
					except socket.timeout:
						if index == 10:
							print "Daten wurden nicht empfangen die ZWEITE %d" % port
							self.__portQueue.put(port)					
							return
						index = index + 1
						if eingabe == "ende":
							break
				(stat, fileNameRecv, fileHashRecv) = antwort.split(";", 2)
				if stat == "LETSGOON":
					con.send("LETSGOON")
					recvData = ""
					bitRate = 0
					bitRateCounter = 0
					while True:
						start = datetime.now().microsecond
						data = con.recv(self.__BUFFERSIZE_FILE)
						if not data:
							break
						recvData = recvData + data
						ende = datetime.now().microsecond
						bitRate = bitRate + float(len(data)*8) / float((ende - start))
						bitRateCounter = bitRateCounter + 1
					print "Transferate %0.3f Mbit/s" % (bitRate / bitRateCounter)
					filoName = "files/testfile" + str(time.clock())
					fileRecv = open(filoName,"wb")
					fileRecv.write(recvData)
					fileRecv.close()
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
		#nachricht an appli das daten nicht gesendet wurden oder return

	def __sendTCP(self, ip, port, filo):
		sockSend = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		sockSend.connect((ip, int(port)))
		hatshi = "hatshiiiiiiir"
		try: 
			nachricht = "LETSGOON;" +  filo + ";" + hatshi
			sockSend.send(nachricht) 
			index = 0
			while True:
				try:
					antwort = sockSend.recv(self.__BUFFERSIZE_FILE)
					break
				except socket.timeout:
					if index == 10:
						print "Daten wurden nicht empfangen die DRITTE %d" % port
						self.__portQueue.put(port)
						#nachricht an appli das daten nicht gesendet wurden					
						return
					index = index + 1
					if eingabe == "ende":
						break
			if antwort == "LETSGOON":
				try:
					sendFile = open(filo, 'rb')
				except:
					etype, evalue, etb = sys.exc_info()
					evalue = etype("Cannot open file: %s" % evalue)
					raise etype, evalue, etb
				while True:
					chunk = sendFile.read(self.__BUFFERSIZE_FILE)
					if not chunk:
						break  # EOF
					sockSend.sendall(chunk)
		except socket.error as msg:
			sockSend.close()
			sockSend = None
			print msg
		finally: 
			sockSend.close()
		#nachricht an appli das datei gesendet wurden oder return

	def __send(self, ip, port, stat, nachricht):
		hatshi = ""
		partQueue = Queue.Queue()
		nachricht = stat + ";" + nachricht
		partSize = self.__BUFFERSIZE_UDP - 38
		lenNachricht = len(nachricht)
		if lenNachricht > ((self.__BUFFERSIZE_UDP - 38) * 255):
			print "Nachricht zu lang"
			return False
		partCount = lenNachricht // (partSize)
		roundCount = partCount
		partLenLast = lenNachricht % (partSize)
		sequNumm = self.__calcHash(str(datetime.now()))
		if partLenLast > 0:
			partCount = partCount + 1
		for i in range(roundCount):
			fromIndex = partSize * i
			toIndex = (partSize * i) + partSize
			partQueue.put((i + 1, partCount, nachricht[fromIndex:toIndex]))
		if partLenLast > 0:
			fromIndex = partSize * (partCount - 1)
			toIndex = (partSize * (partCount - 1)) + partLenLast
			partQueue.put((partCount, partCount, nachricht[fromIndex:toIndex]))
		for i in range(partCount):		
			try:
				sockSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				sendStat = False
				(part, partCount, partNachricht) = partQueue.get()
				partNachricht = str(hex(part)[2:4]) + ";" + str(hex(partCount)[2:4]) + ";" + self.__ip + ";" + str(self.__portRecv) + ";" + sequNumm + ";" +  partNachricht
				hatshi0 = self.__calcHash(partNachricht)
				partNachricht = hatshi0 + ";" + partNachricht
				sockSend.sendto(partNachricht, (ip, port))
			except socket.error as msg:
				sockSend = None
			finally: 
				sockSend.close()
		print "[SEND] %s nach %s:%s\n%s" % (self.__ip, str(ip), str(port), nachricht)
		return sendStat
        
	def __sendUdp(self):
		print "sendUdp start"
		while True:
			try:
				(sendCase, sendIP, sendPort, nachricht) = self.__sendQueue.get(True, 1.0)
				if sendCase == "message":
					sendStat = self.__send(sendIP, sendPort, "OVERSTAT", nachricht)
					if sendStat == False:
						pass
						#Ansage nach oben
				elif sendCase == "fileTransfer":
					sendPortTcp = self.__portQueue.get()
					threadTCP = Thread(target=self.__recvTCP, args=(sendPortTcp, "hallo welt"))
					self.__threadArray.append(threadTCP)
					threadTCP.start()
					self.__send(sendIP, sendPort, "FILETRAN", str(sendPortTcp) + "," + nachricht)
				elif sendCase == "fileTransferOK":
					threadTCP = Thread(target=self.__sendTCP, args=(sendIP, sendPortTCP, nachricht))
					self.__threadArray.append(threadTCP)
					threadTCP.start()
			except Queue.Empty:
				if eingabe == "ende":
					break
		print "sendUdp ende"

	def __calcHash(self, text):
		hatshi = hashlib.md5(text).hexdigest()[:self.__HASHLENGTH]
		return hatshi
    
	def __recvUdp(self):
		print "recvUdp start"
		
		recvDict = {}
		recvDictPack = {}
		
		sockRecv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sockRecv.bind((self.__ip, self.__portRecv))
		sockRecv.settimeout(1.0)
		
		while True:
			try:
				data, addr = sockRecv.recvfrom(self.__BUFFERSIZE_UDP)
				
				(dataHashRecv, data) = data.split(";", 1)
				dataHash = str(self.__calcHash(data))
				if dataHashRecv == dataHash:
					(part, partCount, senderIP, senderPort, sequNumm, nachricht) = data.split(";", 5)
					part = int(part, 16)
					partCount = int(partCount,16)
					
					if (partCount, senderIP, senderPort) in recvDict.keys():
						if recvDict[(partCount, senderIP, senderPort)] != sequNumm:
							recvDict[(partCount, senderIP, senderPort)] = sequNumm
							for i0, i1, i2, i3 in recvDictPack.keys():
								if i2 == senderIP and  i3 == senderPort:
									del recvDictPack[(i0, i1, i2, i3)]
					else:
						recvDict[(partCount, senderIP, senderPort)] = sequNumm
						
					recvDictPack[(part, partCount, senderIP, senderPort)] = nachricht
					if (part == partCount) and (recvDict[(partCount, senderIP, senderPort)] == sequNumm):
						nachricht =  ""
						for i in range(partCount):
							if (i + 1, partCount, senderIP, senderPort) in recvDictPack:
								nachricht = nachricht + recvDictPack[(i + 1, partCount, senderIP, senderPort)]
								del recvDictPack[(i + 1, partCount, senderIP, senderPort)]
						self.__recvUdp2(nachricht, addr, senderIP, senderPort)
						del recvDict[(partCount, senderIP, senderPort)]
						continue
			except socket.timeout:
				if eingabe == "ende":
					break
				continue
		sockRecv.close()
		print "recvUdp ende"

	def __recvUdp2(self, nachricht, addr, senderIP, senderPort):
		print "[RECV] von %s:%s nach %s\n%s" % (addr[0], addr[1], senderIP, nachricht)
		(stat, nachricht) = nachricht.split(";", 1)
		if not(nachricht == ""):
			if stat == "OVERSTAT":
				pass
				#nach oben geben!!!
			elif stat == "FILETRAN":
				(senderPort, nachricht) = nachricht.split(",", 1)
				#nach oben geben!!!
		return True
 

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

n2o = Queue.Queue()
o2n = Queue.Queue()

eingabe = ""

network = Network(ip, portRecv, startTcpPort, countTcpPort, n2o, o2n)
network.run()

while 1:
    eingabe = raw_input("> ") 
    if eingabe == "ende": 
        break
 
sys.exit(-1)
