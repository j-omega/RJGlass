#!/usr/bin/env python
# ----------------------------------------------------------
# aircraft_data MODULE for GlassCockpit procject RJGlass
# ----------------------------------------------------------
# This module handels and stores all aircraft data, and communicated via FSUIPC to FS2004
#
# Copyright 2007 Michael LaBrie
#
#    This file is part of RJGlass.
#
#    RJGlass is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.

#   RJGlass is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ---------------------------------------------------------------


import socket
import csv
import time
from guage import *
import keyboard


	

class data(object):

	
	
	def __init__(self):
		self.count = 0
		self.attitude = attitude_c()
		self.airspeed = airspeed_c()
		#self.radar_alt = 0 # Integer
		self.ias_bug = 220 #Integer
		self.altimeter = altimeter_c()
		self.HSI = HSI_c()
		self.VOR1 = VOR_c("VOR1")
		self.VOR2 = VOR_c("VOR2")
		self.ADF1 = ADF_c("ADF1")
		self.ADF2 = ADF_c("ADF2")
		self.ND = ND_c()
		self.VertSpeed = -800
		#Frame Timer Variables
		self.clock = time.time() 
		self.count2 = 0 #counter used to determine clock cycle
		self.frame_time = 0.01 #Time between frames. 1 / frame_time = FPS (frames per second)
		self.nodata = 0
	def set_UDP(self, port):
		global udpSock
		udpSock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
		udpSock.bind(('', port))
		socket.setdefaulttimeout(1)
		udpSock.settimeout(1)
	def read_UDP(self):
		
		
		def encode(l,signed): #Encode a list of ASCII characters from UDP data to integer
			v = 0
			l = l[::-1] #Reverse list
			neg = False
			first = ord(l[0])
			if (signed) and (first & 0x80): #If number is signed test for negative
				neg = True
				v = first ^ 0xFF
			else:
				v = first
			for i in l[1:]: #Skip first to end
				i = ord(i)
				if neg:
					i = i ^ 0xFF
				v = (v << 8) + i
			if neg:
				v = (v +1 ) * -1
				#v = 10000
			return v
		global udpSock
		#Get Data from UDP
		self.valid = True
		try:
			d, addr = udpSock.recvfrom(1024)
		except socket.timeout:
			print "NO FSX DATA"
			self.valid= False
		if d:
			self.altimeter.value = encode(d[1:3],True)
			self.attitude.bank = encode(d[3:5], True) * -360.0 / 65536
			self.attitude.pitch = encode(d[5:7], True) * -360.0 / 65536
			self.airspeed.IAS = encode(d[7:11], True) / 128.0
			self.HSI.True_Heading = encode(d[11:13], False) * 360.0 / 65536
			self.HSI.Mag_Variation = encode(d[13:15], True) * 360.0 / 65536
			self.HSI.Mag_Heading = self.HSI.True_Heading - self.HSI.Mag_Variation
			self.altimeter.absolute = int(encode(d[15:18], False) * 3.280 / 256) #Meters to Feet
			self.altimeter.pressure = encode(d[18:20], False) * 0.02952 / 16 #Millibars to Inches of Hg
		
	def decode_FSX(self,d):
		
		def True_False(d): #Used to decode a 1 to true and a 0 to false
			print d
			if d==0:
				return False
			else:
				return True
			
		r = csv.reader([d])
		air_list = r.next()
		#air_list = [3000.0, 0.0, 0.0, 120.0, 234.3, 29.92, 0, 0.200, -200, 0, 100, 200, 0, 0, "1", 10.3, "1", 5, -5, 
		#All data gets associated with correct variable.
		self.altimeter.value = int(float(air_list.pop(0)))
		self.attitude.bank = -float(air_list.pop(0))
		self.attitude.pitch = -float(air_list.pop(0))
		self.airspeed.IAS = float(air_list.pop(0))
		self.HSI.Mag_Heading = float(air_list.pop(0))
		self.altimeter.pressure = float(air_list.pop(0)) # Altimeter setting
		self.altimeter.absolute = int(air_list.pop(0)) #Radar Altimeter
		self.airspeed.mach = float(air_list.pop(0))
		self.VertSpeed = int(air_list.pop(0))
		self.attitude.marker.on = int(air_list.pop(0))
		self.VOR1.radial = float(air_list.pop(0))
		self.VOR1.OBS = int(air_list.pop(0))
		self.VOR1.CDI = int(air_list.pop(0))
		self.VOR1.GSI = int(air_list.pop(0))
		#ToFrom
		#self.VOR1.ToFrom = True_False(air_list.pop(0))
		#temp = int(air_list.pop(0))
		#print temp
		#if temp ==1:
		#	self.VOR1.ToFrom = True
		#else:
		#	self.VOR1.ToFrom = False
		self.VOR1.ToFrom = True_False(int(air_list.pop(0)))
		self.VOR1.DME = float(air_list.pop(0))
		#Flight Director
		self.attitude.FD_active=True_False(int(air_list.pop(0)))
		self.attitude.FD_bank=-float(air_list.pop(0))
		self.attitude.FD_pitch=-float(air_list.pop(0))
		#AP Bugs
		self.altimeter.bug = int(air_list.pop(0))
		self.airspeed.bug = int(air_list.pop(0))
		self.HSI.Heading_Bug = int(air_list.pop(0))
	
	def read_FSX_UDP(self):
		
		global udpSock
		#Get Data from UDP
		try:
			d, addr = udpSock.recvfrom(1024)
			self.decode_FSX(d)
			self.comp()
			self.nodata =0
		except:
			print "Error: NO DATA FROM FSX"
			self.nodata+=1
			if self.nodata >2: self.nodata=1 #Used so data will flash, program will only show nodata message is self.nodata =1
		

	def comp_frame_time(self, i):
		if self.count2 >= i:
			t = time.time()
			self.frame_time = (t - self.clock) / self.count2
			self.clock = t
			self.count2 =0
			#print self.frame_time
			
		else:
			self.count2+=1
		
	
	def comp_IAS_accel(self, airspeed, frame_rate):
		#Computes forcastes IAS in 10 seconds for the IAS tape IAS_diff
		#Find difference between new_IAS and last reading
		diff = airspeed.IAS - airspeed.IAS_prev
		airspeed.IAS_prev = airspeed.IAS
		#Add diff reading to list pop oldest one
		airspeed.IAS_list.append(diff)
		airspeed.IAS_list.pop(0)
		a= airspeed.IAS_list
		airspeed.IAS_diff = (sum(a) / len(a)) / frame_rate * 10
	
	def comp(self):
	#Computation section
		if self.airspeed.IAS <=40:
			self.airspeed.IAS_guage = 40
		else: 
			self.airspeed.IAS_guage = self.airspeed.IAS
		if self.altimeter.value < -1000: self.altimeter.value = -1000
		#Radial calc, to bearing
		self.VOR1.bearing = Turn_180(self.VOR1.radial)
		self.attitude.GS = self.VOR1.GSI
		#self.attitude.GS = self.VOR1.GSI
		#IAS Acceleration section
		self.comp_frame_time(20)
		self.comp_IAS_accel(self.airspeed, self.frame_time)
	

	def test(self):
		
		#time.sleep(0.01)
		#self.attitude.bank += 0.1
		#self.attitude.pitch -=0.01
		#self.attitude.pitch = 20.0
		self.comp()
		#self.comp_frame_time(20)
		#self.VOR1.OBS +=1
		#self.VOR1.active = False
		#self.HSI.Mag_Heading =359.7
		#self.HSI.Mag_Heading =1
		#self.airspeed.IAS -= 0.31
		#self.attitude.FD_pitch +=0.01
		#self.attitude.FD_bank +=0.04
		#self.attitude.GS +=1
		self.altimeter.DH.bug = 320
		#self.HSI.Mag_Heading += 0.5
		self.HSI.Heading_Bug  = Check_360(254)
		#self.altimeter.absolute -= 1
		if self.count >=30:
			#self.altimeter.value = self.altimeter.value - 1
			#self.ND.range.down()
			#self.VertSpeed +=10
			#self.VOR1.active= False
			#self.VOR1.ToFrom = False
			#time.sleep(10)
			self.count =0
		#else:
		#	self.HSI.Heading_Bug+=1
	#	self.altimeter.absolute = 200
	#		self.count =0
		self.count +=1 
		
	
class ND_c(data): #Class the handles the Nav Display (ND)
	def __init__(self):
		self.range = range_c()
		
class range_c(ND_c):
	def __init__(self):
		self.index = 6
		self.ranges = [5, 10, 20, 40, 80, 160, 320]  #The ranges possible for ND display 
		self.num_ranges = len(self.ranges)
		self.value = self.ranges[self.index]
		
	def up(self):

		if self.index<(self.num_ranges-1): 	self.index+=1
		self.value = self.ranges[self.index]
		
	def down(self):
		self.index-=1
		if self.index<0: self.index =0
		self.value = self.ranges[self.index]

		
class MDA_DH_c(data): #The class for MDA and DH (They have very similar functions)
	def __init__(self):
		self.bug = 1200
		self.visible = True
		self.selected = True
		self.notify = False #On if MDA_DH notification is on
		self.flash = 0 #Int used for flashing of notifier (MDA use only)
		self.frame_count = 0 #Used for flash delay of MDA notifier
class altimeter_c(data):
	
	def __init__(self):
		self.value = 1400
		self.pressure = 29.82
		self.absolute = 500.0 #Absolute / Radar Altitude (Altitude Above Ground)
		self.MDA = MDA_DH_c()
		self.DH = MDA_DH_c()
		self.bug = 1500
		
		
class HSI_c(data):
	def __init__(self):
		#Constants
		self.NADA =0
		self.VOR = 1
		self.ADF = 2
		self.FMS = 3
		#Variables
		self.Mag_Heading = 0
		self.True_Heading = 0.0
		self.Mag_Variation = 0.0
		self.Mag_Track= 348.0
		self.Heading_Bug = 0
		self.Heading_Bug_Timer = 0 #Used as timer for drawing heading bug when its value changes
		self.Heading_Bug_prev = 0
		self.Bearing1 = self.ADF #Will either be FMS, VOR or ADF
		self.Bearing2 = self.VOR
		
class VOR_c(data):
	#Class for Vor navaids, 1 and 2
	def __init__(self, name):
		self.OBS = 330
		self.CDI = -27
		self.GSI = -27
		self.name = name
		self.active = True
		self.bearing = 200
		self.radial = 20
		self.DME = 0.5
		self.ID = "ATL"
		self.ToFrom = True

class ADF_c(data):
	def __init__(self, name):
		self.bearing = 100
		self.active = True
		self.name = name

class attitude_c(data):
	
	def __init__(self):
		self.pitch = -3.5
		self.bank = 4.0
		self.FD_active = True
		self.FD_pitch = 0.0
		self.FD_bank = 0.0
		self.GS = -127
		self.marker = marker_c()
		
class marker_c(attitude_c):
		def __init__(self):
			#Constants
			self.OM = 1
			self.MM = 2
			self.IM = 3
			
			self.on = self.OM #Which marker is on
			self.count = 0

class airspeed_c(data):
	def __init__(self):
		self.IAS = 120.0
		self.IAS_guage = 140.0
		self.IAS_diff = 10.0 #Pink Line to show accel or decell
		self.IAS_prev = self.IAS
		self.IAS_list = [0] * 40 # This is used to compute IAS accelertation for airspped tape
		self.TAS = 0.0
		self.Mach = 0.0
		self.GS = 0.0
		self.V1 = 60
		self.V2 = 65
		self.VR = 68
		self.VT = 110
		self.bug = 150
		self.VNE = 260 #Never Exceed speed Red line
		self.VS = 220 #Stall speed
		self.mach = 0.451
