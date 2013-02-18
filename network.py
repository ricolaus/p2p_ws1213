import socket
from threading import Thread
import time
import sys
import Queue
import hashlib
from datetime import datetime
import os
import ast
import help_functions

class Network(object): 
	def __init__(self, userFolder, ip, pRecv, startPort, countPort, recvQueue, sendQueue, watcherQueue, mode): 
		self.__ip = ip
		self.__userFolder = userFolder
		self.__recvQueue = recvQueue
		self.__sendQueue = sendQueue
		self.__watcherQ = watcherQueue
		self.__portRecv = pRecv
		self.__mode = mode
		self.__portQueue = Queue.Queue()
		for i in range(countPort): 
			self.__portQueue.put(startPort + i)
		self.__threadArray = []
		self.__HASHLENGTH = 5
		self.__BUFFERSIZE_UDP = 63
		self.__BUFFERSIZE_TCP = 1024
		self.__BUFFERSIZE_FILE = 1024 * 32
		
	def run(self):
		t0 = Thread(target=self.__recvUdp, args=())
		t0.start()
		t1 = Thread(target=self.__sendUdp, args=())
		t1.start()
		sendWatcherThread = Thread(target=self.__sendUdp2Watcher, args=())
		sendWatcherThread.start()
#		if self.__mode == 1:
#			t2 = Thread(target=self.__test1, args=())
#			t2.start()
#			t3 = Thread(target=self.__test2, args=())
#			t3.start()

	def __test1(self):
		print "test1 start"
#		while True:
#			case = random.randint(0, 1)
#			if case == 0:
#				message = ""
#				testRange = random.randint(1, 50)
#				for i in range(testRange): #35 bei 64 Byte
#					message = message + str(random.randint(0, 9))
#				self.__sendQueue.put(("message", "127.0.0.1", self.__portSend, message))
#			else:
#				self.__sendQueue.put(("fileTransfer", "127.0.0.1", self.__portSend, "files/filetrans"))
#			time.sleep(random.uniform(0.1,3.0))
#			if eingabe == "ende":
#				break
		#outgoing ping (o2n) := ("ping", pingID, ttl, hops, ownUsername, ownIP, targetIP, targetPort)
		#self.__sendQueue.put(("ping", 159, 4, 0, "ownUsername", self.__ip, self.__portRecv, "127.0.0.1", self.__portSend))
		#outgoing pong (o2n) := ("pong", id, [(username1, ipP1), (username2, ip2), ...], targetIP, targetPort)
		#self.__sendQueue.put(("pong", 158, "List of (username_n, ip_n)", "127.0.0.1", self.__portSend))
		#outgoing refFL (o2n) := ("refFL", fileList, ownUsername, targetIP, targetPort)
		#self.__sendQueue.put(("refFL", "fileList", "ownUsername", self.__ip, self.__portRecv, "127.0.0.1", self.__portSend))
		#outgoing reqFile (o2n) := ("reqFile", fileName, fileHash, senderIP, targetIP, targetPort)
		#self.__sendQueue.put(("reqFile", "files/filetrans", "fileHash", self.__ip, self.__portRecv, "127.0.0.1", self.__portSend))
		#downgoing sendFile (o2n) := ("sendFile", filePath, targetIP, targetPortUDP, targetPortTCP)
	#	self.__sendQueue.put(("sendFile", "filePath", "127.0.0.1", self.__portSend, 1337))
		print "test1 ende"        
		
	def __test2(self):
		print "test2 start"
		while True:
			try:
				ausgabe = self.__recvQueue.get(True, 1.0)
				print ausgabe
			except Queue.Empty:
				if eingabe == "ende":
					break
				continue
		print "test2 ende"

	def __recvTCP(self, port, fileName, fileHash, filePart):
		try:
			sockRecv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sockRecv.bind(("", port)) 
			sockRecv.settimeout(0.1)
			sockRecv.listen(1)
			filePath = self.__userFolder + "." + fileName + "_" + fileHash
			index = 1
			while True: 
				try:
					con, addr = sockRecv.accept()
					addr = addr
				except socket.timeout:
					if eingabe == "ende":
						break
					if index == 10:
						print "Daten wurden nicht empfangen die ERSTE %d" % port
						self.__recvQueue.put(("fileTransRecv", fileName, fileHash, filePart, False))
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
							self.__recvQueue.put(("fileTransRecv", fileName, fileHash, filePart, False))					
							return
						index = index + 1
						if eingabe == "ende":
							break
				(stat, fileNameRecv) = antwort.split(";", 1)
				fileNameRecv = fileNameRecv
				if stat == "LETSGOON":
					con.send("LETSGOON")
					recvData = ""
					bitRate = 0
					bitRateCounter = 1
					while True:
						start = datetime.now().microsecond
						try:
							data = con.recv(self.__BUFFERSIZE_FILE)
						except socket.error as msg:
							# print msg
							data = "exception thrown"
						if data == "exception thrown":
							continue 
						if not data:
							break
						recvData = recvData + data
						ende = datetime.now().microsecond
						# bitRate = bitRate + float(len(data)*8) / float((ende - start))
						bitRateCounter = bitRateCounter + 1
					print "Transferate %0.3f Mbit/s" % (bitRate / bitRateCounter)
					filoName = "part" + str(filePart)
					if not os.path.isdir(filePath):
						os.mkdir(filePath)
					#print "%s %s %s" % (filePath , filoName, filePart)
					fileRecv = open(filePath  + "/" + filoName,"wb")
					fileRecv.write(recvData)
					fileRecv.close()
					#print datetime.now().microsecond
					self.__portQueue.put(port)
					self.__recvQueue.put(("fileTransRecv", fileName, fileHash, filePart, True))
					break
		except socket.error as msg:
			print "recvTCP: " + str(msg)
		finally: 
			sockRecv.close()
		#nachricht an appli das daten nicht gesendet wurden oder return

	def __sendTCP(self, ip, portUDP, portTCP, filePath, filePart):
		sockSend = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		#print ip + str(portTCP)
		sockSend.connect((ip, int(portTCP)))
		try: 
			nachricht = "LETSGOON;" +  filePath
			sockSend.send(nachricht) 
			index = 0
			filePart = int(filePart)
			filePart = 1
			while True:
				try:
					antwort = sockSend.recv(self.__BUFFERSIZE_FILE)
					break
				except socket.timeout:
					if index == 10:
						print "Daten wurden nicht gesendet die DRITTE %d" % portTCP
						self.__portQueue.put(portTCP)
						self.__recvQueue.put(("fileTransSend", ip, portUDP, filePath, False))
						#nachricht an appli das daten nicht gesendet wurden					
						return
					index = index + 1
					if eingabe == "ende":
						break
			if antwort == "LETSGOON":
				if filePart > 0:
					chunkSize = self.__BUFFERSIZE_FILE
					sendData = help_functions.readFilePart(filePart, filePath)
					if chunkSize >= len(str(sendData)):
						sockSend.sendall(str(sendData))
						self.__recvQueue.put(("fileTransSend", ip, portUDP, filePath, True))
					else:
						print "Partsize groesser als BufferSize"
						chunkCount = len(str(sendData)) // chunkSize
						chunkLenLast = len(str(sendData)) % (chunkSize)
						if chunkLenLast > 0:
							chunkCount = chunkCount + 1
							
						for i in range(chunkCount):
							sockSend.sendall(str(sendData[i*chunkSize:(i+1)*chunkSize]))
						self.__recvQueue.put(("fileTransSend", ip, portUDP, filePath, True))
				elif filePart == 0:
					sendFile = open(filePath, 'rb')
					while True:
						chunk = sendFile.read(self.__BUFFERSIZE_FILE)
						if not chunk:
							break  # EOF
						sockSend.sendall(chunk)
					self.__recvQueue.put(("fileTransSend", ip, portUDP, filePath, True))
		except socket.error as msg:
			print "sendTCP: " + str(msg)
		finally: 
			sockSend.close()
		#nachricht an appli das datei gesendet wurden oder return

	def __send(self, ip, port, nachricht):
		partQueue = Queue.Queue()
		nachricht = nachricht
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
				print msg
			finally: 
				sockSend.close()
		#print "[SEND] %s nach %s:%s\t%s" % (self.__ip, str(ip), str(port), nachricht)
		return sendStat	
	
	def __sendUdp(self):
		print "sendUdp start"
		while True:
			try:
				sendTuple = self.__sendQueue.get(True, 0.1)
				
				print "[SEND] %s %s %s %s" % (self.__userFolder, sendTuple[0], str(sendTuple[len(sendTuple) - 1]), str(sendTuple[1]))
				#print sendTuple
				#Ping
				#outgoing ping (o2n) := ("ping", pingID, ttl, hops, ownUsername, ownIP, ownPort, targetIP, targetPort)
				#TODO: ownPort fehlt
				if sendTuple[0] == "ping":
					sendIP = sendTuple[7]
					sendPort = sendTuple[8]
					sendTuple = sendTuple[:7]
					sendTuple = self.tupleToString(sendTuple)
					#ping (n2n) := ("ping", pingID, ttl, hops, sendUsername, sendIP, sendPort)
					sendStat = self.__send(sendIP, sendPort, sendTuple)
				#Pong
				#outgoing pong (o2n) := ("pong", id, [(username1, ipP1), (username2, ip2), ...], targetIP, targetPort)
				elif sendTuple[0] == "pong":
					sendIP = sendTuple[3]
					sendPort = sendTuple[4]
					sendTuple = sendTuple[:3]
					sendTuple = self.tupleToString(sendTuple)
					#pong (n2n) := ("pong", id, [(username1, ipP1), (username2, ip2), ...])
					sendStat = self.__send(sendIP, sendPort, sendTuple)
				#RefFL (refresh filelist)
				#outgoing refFL (o2n) := ("refFL", fileList, ownUsername, ownIP, ownPort, targetIP, targetPort)
										#("refFL", "fileList", "ownUsername", self.__ip, self.__portRecv, "127.0.0.1", self.__portSend)
				elif sendTuple[0] == "refFL":
					sendIP = sendTuple[5]
					sendPort = sendTuple[6]
					sendTuple = sendTuple[:5]
					sendTuple = self.tupleToString(sendTuple)
					#refFL (n2n) := ("refFL", fileList, senderUsername, senderIP, senderPort)
					#TODO: IP und Port aendern
					sendStat = self.__send(sendIP, sendPort, sendTuple)
				#reqFile (request file)
				#outgoing reqFile (o2n) := ("reqFile", fileName, fileHash, filePart, senderIP, senderPort, targetIP, targetPortTCP)
				elif sendTuple[0] == "reqFile":
					sendIP = sendTuple[6]
					sendPort = sendTuple[7]
					sendTuple = sendTuple[:6]
					fileName = sendTuple[1]
					fileHash = sendTuple[2]
					filePart = sendTuple[3]
					listenPortTCP = self.__portQueue.get()
					threadTCP = Thread(target=self.__recvTCP, args=(listenPortTCP, fileName, fileHash, int(filePart)))
					self.__threadArray.append(threadTCP)
					threadTCP.start()
					sendTuple = self.tupleToString((sendTuple) + (listenPortTCP,))
					#reqFile (n2n) := ("reqFile", fileName, fileHash, senderIP, listenPortTCP)
					sendStat = self.__send(sendIP, sendPort, sendTuple)
				#sendFile (permission to network layer to send the file)
				#downgoing sendFile (o2n) := ("sendFile", filePath, partNumm, targetIP, targetUDP, targetPortTCP)
				elif sendTuple[0] == "sendFile":
					sendIP = sendTuple[3]
					sendPortUDP = sendTuple[4]
					sendPortTCP = sendTuple[5]
					partNumm = sendTuple[2]
					filePath = sendTuple[1]
					threadTCP = Thread(target=self.__sendTCP, args=(sendIP, sendPortUDP, sendPortTCP, filePath, partNumm))
					self.__threadArray.append(threadTCP)
					threadTCP.start()
				#print sendStat
	#			if sendCase == "message":
	#				sendStat = self.__send(sendIP, sendPort, "OVERSTAT", nachricht)
	#				if sendStat == False:
	#					pass
	#					#Ansage nach oben
	#			elif sendCase == "fileTransfer":
	#				sendPortTcp = self.__portQueue.get()
	#				threadTCP = Thread(target=self.__recvTCP, args=(sendPortTcp, "hallo welt", "hash"))
	#				self.__threadArray.append(threadTCP)
	#				threadTCP.start()
	#				self.__send(sendIP, sendPort, "FILETRAN", str(sendPortTcp) + "," + nachricht)
	#			elif sendCase == "fileTransferOK":
	#				threadTCP = Thread(target=self.__sendTCP, args=(sendIP, sendPortTCP, nachricht))
	#				self.__threadArray.append(threadTCP)
	#				threadTCP.start()
			except Queue.Empty:
				if eingabe == "ende":
					break
		print "sendUdp ende"
		
	def __sendUdp2Watcher(self):
		print "sendUdp2Watcher start"
		while True:
			try:
				sendTuple = self.__watcherQ.get(True, 1.0)
				
				print "[SEND] %s %s %s" % (self.__userFolder, sendTuple[0], '1337')
				# sending neighbor list
				# neighbors (o2n) := ("neighbors", sendUsername, neighborList, fileCount)
				if sendTuple[0] == "neighbors":
					sendIP = "127.0.0.1"
					sendPort = 1337
					sendTuple = self.tupleToString(sendTuple)
					self.__send(sendIP, sendPort, sendTuple)
			except Queue.Empty:
				if eingabe == "ende":
					break
		print "sendUdp2Watcher ende"
		
	def tupleToString(self, tup):
		string = tup[0]
		for i in range(1, len(tup)):
			string = string + ";" + str(tup[i])
		return string

	def __calcHash(self, text):
		hatshi = hashlib.md5(text).hexdigest()[:self.__HASHLENGTH]
		return hatshi
	
	def __recvUdp(self):
		print "recvUdp start"
		recvDict = {}
		recvDictPack = {}
		sockRecv = None
		try:
			sockRecv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sockRecv.bind((self.__ip, self.__portRecv))
			sockRecv.settimeout(0.1)
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
		except socket.error as msg:
			print msg
		finally: 
			sockRecv.close()
			sockRecv = None
		print "recvUdp ende"
	
	#reqFile (request file)
	#incoming reqFile (n2o) := ("reqFile", fileName, fileHash, senderIP, senderPortUDP , senderPortTCP)
	
	def stringToTuple(self, string):
		t = tuple(string.split(';'))
		return t

	def __recvUdp2(self, nachricht, addr, senderIP, senderPort):
		(stat, nachricht) = nachricht.split(";", 1)
		print "[RECV] %s %s %s" % (self.__userFolder, stat, senderPort)
		if not(nachricht == ""):
			#Ping
			#ping (n2n) := ("ping", pingID, ttl, hops, sendUsername, sendIP, sendPort)
			#TODO: sendPort fehlt noch
			if stat == "ping":
				(pingID, ttl, hops, senderUsername, senderIP, senderPort) = self.stringToTuple(nachricht)
				pingID = int(pingID)
				ttl = int(ttl)
				hops = int(hops)
				#incoming ping (n2o) := ("ping", pingID, ttl, hops, senderUsername, senderIP, senderPort)
				#TODO: senderPort fehlt
				self.__recvQueue.put((stat, pingID, ttl, hops, senderUsername, senderIP, senderPort))
			#Pong
			#incoming pong (n2o) := ("pong", id, [(username1, ip1), (username2, ip2), ...])
			elif stat == "pong":
				(pongID, peerList) = self.stringToTuple(nachricht)
				pongID = int(pongID)
				peerList = ast.literal_eval(peerList)
				#pong (n2n) := ("pong", id, [(username1, ipP1), (username2, ip2), ...])
				#TODO: peerList konvertieren
				self.__recvQueue.put((stat, pongID, peerList))
			#RefFL (refresh filelist)
			#refFL (n2n) := ("refFL", fileList, senderUsername, senderIP, senderPort)
			elif stat == "refFL":
				(fileList, senderUsername, senderIP, senderPort) = self.stringToTuple(nachricht)
				senderPort = int(senderPort)
				fileList = ast.literal_eval(fileList)
				#incoming refFL (n2o) := ("refFL", fileList, senderUsername, senderIP, senderPort)
				#TODO: fileList konvertieren
				self.__recvQueue.put((stat, fileList, senderUsername, senderIP, senderPort))
			#reqFile (request file)
			#reqFile (n2n) := ("reqFile", fileName, fileHash, senderIP, listenPortTCP)
			elif stat == "reqFile":
				(fileName, fileHash, filePart, senderIP, senderPort, senderPortTCP) = self.stringToTuple(nachricht)
				senderPortTCP = int(senderPortTCP)
				#incoming reqFile (n2o) := ("reqFile", fileName, fileHash, senderIP, senderPortTCP)
				self.__recvQueue.put((stat, fileName, fileHash, filePart, senderIP, senderPort, senderPortTCP))
				#downgoing sendFile (o2n) := ("sendFile", filePath, targetIP, targetPortTCP)
				#self.__sendQueue.put(("sendFile", fileName, senderIP, senderPortTCP))
				#nach oben geben!!!
		return True

#if len(sys.argv) < 5:
#	print 'Prgramm wie folgt starten:'
#	print 'Modus: 1 --> "Daten senden" 2 --> "keine Daten senden"'
#	print 'python network.py [IP] [PortSend] [PortRecv] [Modus]'
#	sys.exit()
#portSend = int(sys.argv[3])
#mode = int(sys.argv[4])

#n2o1 = Queue()
#o2n1 = Queue()
#n2o2 = Queue()
#o2n2 = Queue()
#
eingabe = ""
#
#network2 = Network("localhost", 50001, 50000, 60010, 10, n2o2, o2n2, 2)
#network2.run()
#time.sleep(0.2)
#network1 = Network("localhost", 50000, 50001, 60000, 10, n2o1, o2n1, 1)
#network1.run()





#if path.exists("files/filetrans"):
#	fo = open("files/filetrans", "r")
#	text = fo.readline();
#	print "1" + text
#	text = fo.readline();
#	print "2" + text
#	text = fo.readline();
#	print "3" + text
#	text = fo.readline();
#	print "4" + text
#	fo.close()
#else:
#	fo = open("files/filetrans", "wb")
#	text = ""
#	for i in range(1024):
#		text = text + chr(random.randint(33, 126))
#	fo.write("<fileName>\n")
#	fo.write("<fileHash>\n")
#	fo.write("<partCount>\n")
#	fo.write("<partList>\n")
#	fo.close()
	


#
#while 1:
#    eingabe = raw_input("> ") 
#    if eingabe == "ende": 
#        break
# 
#sys.exit(-1)
