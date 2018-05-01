#!/usr/bin/env python
# ----------------------------------------------------------
# Testing for SimConnect
# ----------------------------------------------------------
# This module handels and stores all aircraft data, and communicated via FSUIPC to FS2004
#
# 
# ---------------------------------------------------------------

import threading 
import time
import struct
import config
#from socket import *
import socket
#Constants
#DataTypes
INT32 = 1
INT64 = 2
FLOAT32 = 3
FLOAT64 = 4
STRING8 = 5
STRING32 = 6
STRING64 = 7
STRING128 = 8
STRING256 = 9
#Header length
HEADER_len = 12

class data_obj(object):
	#Used to make a object for Definition to link to
	def __init__(self, value):
		self.value = value
		self.adjusted = value #Used incase value needs to be adjusted from data inputed from FSX.

class event_obj(object):
	#Used to hold send event, with its data
	def __init__(self,value):
		self.value = value
		self.event_id = 0 #Set for 0 initially, will be equal to index of event list for this object
		self.update = False #Can be used  to tell when to update data to FSX.
		
class DataRequest(object):
	#Attempt to store all value as data definition objects
	def __init__(self, SimCon, definition, name, unit, type, func=None):
		#Create Data Definition and Add it to 
		#First send via TCP to Simconnect
		self.func = func
		self.value = 0
		d = struct.pack('<I', definition) + SimCon.string256(name) + SimCon.string256(unit)
		e = d + struct.pack('<iii', type, 0, -1)
		SimCon.client.send(e, 0x0c)
		if type == FLOAT32:
			self.value = 0.0
		#Add lists to Simconnect to keep track of definition
		#SimCon.add_DataDefinition(self)
	#def __get__(self, obj, objtype):
	#	print "Iam being used"
	#	return self.value
	def get(self):
		return self.value

class SimEvent(object):
	def __init__(self, SimCon, eventid, name, data):
		#Mapit on Simconnect
		d = struct.pack('<I', eventid) + SimCon.string256(name)
		SimCon.client.send(d, 0x04)
		self.SimCon = SimCon
		#self.group_id = groupid
		self.eventid = eventid
		self.data = data
	def send(self):
		#print self.eventid, self.data.value
		#print "%r" %self.data
		d = struct.pack('<iiiii', 0, self.eventid, self.data.value, 1, 16)
		self.SimCon.client.send(d, 0x05)
	

class EventList(object):
		def __init__(self,SimCon):
			self.list=[]
			self.prioirty_list = [] #The id's of events that have just changed will be added here.
			self.group_id = id
			self.SimCon = SimCon
			self.count = 1
			self.cycle_count = 0
			self.cycle_timer = 0
		def add(self, name, data):
			t = SimEvent(self.SimCon, self.count, name, data)
			data.event_id = len(self.list) #Get index of where event id will be placed in list
			self.list.append(t) #Add it to end of list
			#self.list.append(SimEvent(self.SimCon, eventid, name))
			
			#AddClientEventToNotificationGroup
			#d = struct.pack('<iii', self.group_id, self.count, 0)
			#self.SimCon.client.send(d, 0x07)
			self.count +=1
			#return t
			
		def cycle(self):
			#Cycle through all of the data in this notification one by one, to make sure data is correct
			self.cycle_timer +=1
			if self.cycle_timer  == 5:
				self.cycle_timer = 0
				self.cycle_count += 1
				if self.cycle_count >= len(self.list):
					self.cycle_count = 0
				self.list[self.cycle_count].send()
				#self.list[0].send()
		def send_updates(self):
			#Scans through group, if any have update = True, then send data to FSX and reset update flag.
			for item in self.list:
				if item.data.update == True:
					item.data.update = False
					item.send()
		def set_priority(self, priority):
			d = struct.pack('<ii', self.group_id, priority)
			#self.SimCon.client.send(d, 0x09)
			time.sleep(8)
			
class DataDefinition(object):
	#Period Constants
	NEVER = 0
	ONCE = 1
	VISUAL_FRAME = 2
	SIM_FRAME = 3
	SECOND = 4
	#Object_ID Constants
	USER = 0
	#Flags Constant
	DEFAULT = 0
	DATA_CHANGED = 1
	
	
	
	#Class to store data definition in list
	def __init__(self, SimCon, id):
		self.list=[]
		self.objlist=[]
		self.id = id
		self.unpack_s = '<' #Always little edian
		self.SimCon = SimCon
	def add(self, name, unit, type, obj, func=None):
		simobj = DataRequest(self.SimCon, self.id, name, unit, type, func)
		#print self.id
		self.list.append(simobj)
		self.objlist.append(obj)
		#print obj
		#print self.objlist
		#Add apporpriate type to unpack string
		temp = ''
		if type == FLOAT32:
			temp = 'f'
		elif type == FLOAT64:
			temp = 'd'
		elif type == INT32:
			temp = 'i'
		elif type == STRING8:
			temp = '8s'
		else:
			print "ERROR: Type Not Found"
			#raise
		self.unpack_s += temp
		
		#return simobj
	def request(self, request_id, object_id, period, flag =0, orgin =0, interval =0, limit =0):
		#Request Data on SimObject 0xe
		d = struct.pack('<iiiiiiii', request_id, self.id, object_id, period, flag, orgin, interval, limit)
		self.SimCon.client.send(d, 0xe)
		
class SimConnect_Client_c(threading.Thread):
	
	def string256(self, s): #Takes a string and returns it padded to 256
		return s.ljust(256, chr(0))
	
	def __init__(self, name, protocol, FSXname, majorversion, minorversion, subversion, recieve):
		self.protocol = protocol
		self.FSX_subversion = subversion
		self.FSX_majorversion = majorversion
		self.FSX_minorversion = minorversion
		self.FSX_name = FSXname
		self.app_name = name
		self.clock = time.time()
		self.count = 0
		self.kill_timer = 0
		threading.Thread.__init__(self) 
		self.read_buffer = ''
		self.packet_data = []
		self.go = True
		self.recieve = recieve
	def attach_header(self, data, protocol, type, num):
		size = len(data)
		t = type | 0xF0000000
		s = struct.pack('<IIII', size + 16, protocol, t, num)
		final = s + data
		return final
	
	def send(self, data, type):
		#Send the data, will add header, type is type of command
		self.count += 1 #increment count, used to just number requests sent to FSX
		mike = self.attach_header(data, self.protocol, type, self.count)
		self.s.send(mike)
		
	
		
	def connect(self, addr, port):
	#Attempts to connect to FSX.
		
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#self.s.settimeout(config.timeout)
		self.s.connect((addr, port))
		
		#Send connection header
		#self.s.settimeout(None)
		self.s.settimeout(config.timeout)
		#self.s.setblocking(0)
		name = self.FSX_name[::-1] #The 3 letter name abbriviation is inverted.
		init_string= self.string256(self.app_name) + struct.pack('<IccccIIII', 0, chr(0), name[0], name[1], name[2], self.FSX_majorversion, self.FSX_minorversion, self.FSX_subversion, 0)
		
		self.send(init_string, 0x01) #The initial connect attempt to FSX.

	def close(self):
		self.s.close()

	def run(self):
		
		def reset_timer():
			#used to reset the kill timer.
			#Called from RJGlass to reset timer, if timer isn't reset then thread will die.
			self.kill_timer = 0
		def decode_header(s):
				#Decode 1st 12 bytes for the header
				#out[0] length of packet out[1] protocol out[2] type of recieve packet
				t = s[:HEADER_len]
				#print "%r" %t
				out = struct.unpack('<III', t)
				#print "Decode Header", out
				return out	
			
		def decode_data(length, packet_type):
			#Used to look for and read anydata that is coming in.
			#Take data from buffer minus header
			data = self.read_buffer[12:length]
			self.read_buffer = self.read_buffer[length:]
			#print "%r" %data
			self.packet_data.append([packet_type, data]) 
			#print "PD", self.packet_data
			return len(self.packet_data)
		
			#print self.packet_data
		#Begin self.receive()
		self.go = True
		print "SERVER STARTING"
		while self.go:
		#print time.time()-self.clock
			#try:
			if self.recieve:
				try:
					r = self.s.recv(1024)
				except socket.timeout:
					print "SERVER TIMED OUT (Will ReTry)"
			else:
				r = ''
			#r =self.s.recv(1024)
			#print "%r" %r
			#self.read_buffer = self.read_buffer + r
			self.read_buffer = r
			#print "Recived Bytes", len(r)
			#except:
			#	pass
			#self.kill_timer += 1 #This is used to kill thread, if RJGlass crashes, or locks up.
			#if self.kill_timer>200:
			#	self.go = False
		#	print "Error: No Data to Recieve"
				
			l = len(self.read_buffer)
			while l>=12: #If not atleast 12bytes than no buffer.
				out = decode_header(self.read_buffer)
				if out[1]== self.protocol: #Check to see if protocol is correct
					status = True #Used in return value
					#print "Header ", out
					if l>=out[0]: #Make sure buffer is large enough for entire data
						num = decode_data(out[0], out[2]) #The length and type is send to decode data
						l = len(self.read_buffer)
						if num > 30: #If data is not being read then close thread.
						#This is so the thread wont run forever.
							self.go = False
							print "RJGlass is not reading input buffer, exiting client thread."
						#If data is decoded it will be sent to self.packet_data list.
						#print time.time()-self.clock, out[0], out[2]
					else:
						print "Error: Length not correct" , l, out[0]
						l=0 #bad data forces while loop to exit
				else: #If protocol wrong then error in transmission clear buffer
					#self.read_buffer = ''
					l=0 #forces loop to exit
					print "Error in Data: Protocol Wrong,  Read_Buffer cleared" , out[1]
			
			#Check read buffer
			#print "%r" %self.read_buffer
			#print "Break"
			#time.sleep(3)
			#Quit thread
		self.s.close()
		
class SimConnect(object):
	
	def Load_Flightplan(self, fileloc):
		#Request Data on SimObject 0xe
		#d = self.string256(fileloc)
		d = fileloc.ljust(260, chr(0))
		self.client.send(d, 0x3f)
	
	def create_DataDefinition(self, id):
		t = DataDefinition(self,id)
		self.data_dict[id] = t
		return t
		
	def create_EventList(self):
				e = EventList(self)
				return e	
	
	def string256(self, s): #Takes a string and returns it padded to 256
		return s.ljust(256, chr(0))
	
	
	
	def __init__(self, name, FSX_version, recieve):
		#Initalizes SimConnect
		#Depending on your FSX_version you are connecting to, need to set protocol etc.
#		self.read_buffer = ''
		self.data_dict = {}
		if FSX_version == config.FSXSP0:
			FSX_subversion = 60905
			FSX_major_version = 10
			FSX_minor_version = 0
			FSX_name = "FSX"
			protocol = 2
		elif FSX_version == config.FSXSP1:
			FSX_subversion = 61355
			FSX_major_version = 10
			FSX_minor_version = 0
			FSX_name = "FSX"
			protocol = 3
		elif FSX_version == config.FSXSP2:
			FSX_subversion = 61259
			FSX_major_version = 10
			FSX_minor_version = 0
			FSX_name = "FSX"
			protocol = 4
		elif FSX_version == config.ESP :
			FSX_subversion = 20
			FSX_major_version = 1
			FSX_minor_version = 0
			FSX_name = "ESP"
			protocol = 4
			
		#self.app_name = name
		self.client = SimConnect_Client_c(name, protocol, FSX_name, FSX_major_version, FSX_minor_version, FSX_subversion, recieve)
		self.data_list = [] #Sets up data list will be object eventually

	def connect(self, addr, port, connect):
		self.client.connect(addr,port)
		if connect: self.client.start()
	
	def close(self):
		#Closes the connection with FSX
		self.client.close()
	
	def receive(self):
	
	
		def decode_packet(packet_data):
			packet_type = packet_data[0]
			data = packet_data[1]
			#print packet_type, data
			if packet_type == 8: #Receive data on SimObject
				#print "%r" %data
				#Get 1st 7 ints
				out = struct.unpack('<7I', data[:28])
				request_id = out[0]
				id = out[2]
				#print out
				#Get the correct data_definition
				data_def = self.data_dict[id]
				parsed = struct.unpack(data_def.unpack_s, data[28:])
				#Set values
				i =0
				#print parsed
				for v in parsed:
					if data_def.list[i].func == None:
						data_def.objlist[i].value = v
					else:
						data_def.objlist[i].value = data_def.list[i].func(v)
					#print data_def.objlist[i], v
					i+=1
				return id
			else:
				print "Error Type Equals", packet_type
				return -1
			
			
		status = False	#Check packet data to see if any data is in there.
		define_id = [] #Empty list
		while len(self.client.packet_data) > 0:
			#print "Decoding Packet", len(self.client.packet_data)
			status = True
			define_id.append(decode_packet(self.client.packet_data.pop(0)))

		return define_id
	
if __name__ == '__main__':
	s = SimConnect('RJGlass_As', 2, True)
	s.connect('192.168.1.37', 1500, True)
	s.receive()
	s.Load_Flightplan('DTWCVG')
	#s.definition_0 = s.create_DataDefinition(7)
	#airspeed = data_obj(0.00)
	#s.definition_0.add("Airspeed Indicated", "knots", FLOAT32, airspeed)
	#print airspeed.value
	#s.receive()
	#alt = data_obj(200.0)
	#s.definition_0.add("Indicated Altitude", "feet", FLOAT32, alt)
	#AGL = alt.get
	#s.receive()
	#s.definition_0.request(4, DataDefinition.USER, DataDefinition.VISUAL_FRAME, interval = 10)
	#while True:
	time.sleep(13)
	s.close()