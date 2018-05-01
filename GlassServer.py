#!/usr/bin/env python
# ----------------------------------------------------------
# Glass Server
# ----------------------------------------------------------
# 
#
# use nc localhost 5004 in linux to test

# ---------------------------------------------------------------

import threading 
import time
import struct
import config
#from socket import *
import socket, select
import pickle
import FMS_control
#import aircraft
#Constants


import SocketServer

class global_c(object):
	def __init__(self):
		self.value = None
	def set(self,value):
		self.value = value
g = global_c()		

def get_global():
	return g.value
def set_global(value):
	g.set(value)



class EchoRequestHandler(SocketServer.BaseRequestHandler):
	
	#def __init__(self, aircraft):
	#	self.aircraft = aircraft
		
	def setup(self):
		print self.client_address, 'connected!'
		self.request.send('hi ' + str(self.client_address) + '\n')
		#self.socket.settimeout(10)
		self.request.settimeout(10)
	def handle(self):
		aircraft = get_global()
		while aircraft.quit_flag==False:
			try:
				data = self.request.recv(1024)
			except socket.timeout:
				print self.client_address, "TIMED OUT"
				return
			#self.request.send(get_data())
			d = data.strip()
			if 'FMS' in d:
				o = aircraft.FMS.get_Pickle()
				self.request.send(o)
			else:
				self.request.send("NONE")
			if 'BUTTON' in d:
				loc = d.find('BUTTON') + 6
				aircraft.FMS.button_pressed.append(d[loc:])
				
			#print aircraft.altimeter.indicated.value
			#s = aircraft.PFD_pickle.pickle_string()
			
			if data.strip() == 'bye':
				return

	def finish(self):
		print self.client_address, 'disconnected!'
		self.request.send('bye ' + str(self.client_address) + '\n')

class Glass_Server_c(threading.Thread):
	
	def __init__(self, aircraft_data):
		#self.port = listen_port
		#This is only required because I couldn't find out a way to pass aircraft_data into the socketserver's handler
		set_global(aircraft_data)
		self.aircraft_data= aircraft_data
		threading.Thread.__init__(self)

	def run(self):
		
		server = SocketServer.ThreadingTCPServer(('localhost', config.server_port), EchoRequestHandler)
		#server.socket.settimeout(5)
		while self.aircraft_data.quit_flag == False:
			r,w,e = select.select([server.socket], [], [], 5)
			if r:
				server.handle_request()
				
	
		server.socket.close()
		print "QUITTING"	
			
if __name__ == '__main__':
	aircraft_data = aircraft.data()
	glass = Glass_Server_c(aircraft_data)
	glass.start()
	print "SERVER is RUNNING"
	time.sleep(10)