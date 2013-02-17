import socket
from threading import Thread
import Queue
import hashlib
import ast


class Network(object): 
	def __init__(self, ip, pRecv, recvQueue): 
		self.__ip = ip
		self.__portRecv = pRecv
		self.__recvQueue = recvQueue
		self.__portQueue = Queue.Queue()
		self.__threadArray = []
		self.__HASHLENGTH = 5
		self.__BUFFERSIZE_UDP = 63
		self.__BUFFERSIZE_TCP = 1024
		self.__BUFFERSIZE_FILE = 65536
		
	def run(self):
		t0 = Thread(target=self.__recvUdp, args=())
		t0.start()
		
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
		except socket.error as msg:
			print msg
		finally: 
			sockRecv.close()
			sockRecv = None
		print "recvUdp ende"
	

	def __recvUdp2(self, nachricht, addr, senderIP, senderPort):
		print "[RECV] von %s:%s nach %s\t%s" % (addr[0], addr[1], senderIP, nachricht)
		(stat, nachricht) = nachricht.split(";", 1)
		if not(nachricht == ""):
			#Ping
			#ping (n2n) := ("ping", pingID, ttl, hops, sendUsername, sendIP, sendPort)
			#TODO: sendPort fehlt noch
			if stat == "ping":
				(pingID, ttl, hops, senderUsername, senderIP, senderPort) = ast.literal_eval(nachricht)
				pingID = int(pingID)
				ttl = int(ttl)
				hops = int(hops)
				#incoming ping (n2o) := ("ping", pingID, ttl, hops, senderUsername, senderIP, senderPort)
				#TODO: senderPort fehlt
				self.__recvQueue.put((stat, pingID, ttl, hops, senderUsername, senderIP, senderPort))
		return True

eingabe = ""
