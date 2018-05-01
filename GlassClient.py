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
#import aircraft
#Constants



class client(object):
	def __init__(self, address, port):
		self.IPaddr = address
		self.port = port
	
	def connect(self):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((self.IPaddr, self.port))
		print "CONNECTING to ", self.IPaddr, self.port
		self.s.settimeout(10)
	def get_data(self, right_screen, left_screen, FMS):
			
		out_s = right_screen.guage_active.name + left_screen.guage_active.name
		if len(FMS.button_pressed) > 0:
			b_name = FMS.button_pressed.pop(0)
			out_s += "BUTTON" + b_name
		
		print "%r" %out_s
		self.s.send(out_s)
		
		r = self.s.recv(4096)
		#print "Recieved %r" %r
		return r
		
