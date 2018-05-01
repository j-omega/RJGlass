#!/usr/bin/env python
# ----------------------------------------------------------
# aircraft_data MODULE for GlassCockpit procject RJGlass
# ----------------------------------------------------------
# This module handels and stores all aircraft data, and communicated via Simconnect to FSX
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
import config
from guage import *
import keyboard
import math
from PySimConnect import *
import sounds
import formula
import autopilot
import pickle
import GlassServer
import FMS_control
from PFDND_data import *
from EICAS_data import *

#def __init__(self):
	#self.data = data()

class data(object):

	
	def __init__(self, PFD):
		self.global_time = 0.0 #Used for timing reasons. 
		self.prev_time = 0.0 #Used for delta time calc in comp function.
		self.count = 0
		self.comp_time = 0.0 #Used for timer for comp_second function.
		self.quit_flag = False #If True then RJGlass will exit
		self.attitude = attitude_c()
		
		self.FMS = FMS_control.FMS_c(self)
		self.declutter = declutter_c()
		self.airspeed = airspeed_c()
		self.aileron_pos= data_obj(0)
		self.elev_trim = data_obj(0)	
		self.AP = autopilot.AP_c(PFD, self.attitude, self.global_time, self)
		self.AP.aileron_pos = event_obj(0)
		self.AP.elevtrim_pos = event_obj(0)
		#self.radar_alt = 0 # Integer
		self.ias_bug = 220 #Integer
		self.altimeter = altimeter_c()
		self.flaps = flaps_c()
		self.fuel = fuel_c()
		self.gear = Gear_c()
		self.brakes = Brakes_c()
		self.trim = Trim_c()
		self.APU = APU_c()
		self.onground = data_obj(1)
		self.total_weight = data_obj(0)
		self.OAT = data_obj(25.0)
		self.HSI = HSI_c()
		self.NAV = NAV_c()
	#	self.ADF1 = ADF_c("ADF1")
	#	self.ADF2 = ADF_c("ADF2")
		self.ND = ND_c()
		self.VSI = data_obj(-800)
		
		self.Eng_1 = Engine_c(1)
		self.Eng_2 = Engine_c(2)

		self.TEST = event_obj(32000)
		self.TEST4 = data_obj(100)
		self.TEST2 = event_obj(100)
		#self.LatLong = (math.radians(41.9217),math.radians(-84.0825))
		self.Latitude = data_obj(math.radians(32.36))
		self.Longitude = data_obj(math.radians(-91.7))
		self.PFD_pickle = PFD_pickle_c(self)
		self.EICAS_pickle = EICAS_pickle_c(self)
#		self.LatLong = (0.73675821079214898, -1.4550227732038261)
		#Frame Timer Variables
		self.clock = time.time() 
		
		self.count2 = 0 #counter used to determine clock cycle
		self.frame_time = 0.01 #Time between frames. 1 / frame_time = FPS (frames per second)
		self.nodata = False
		self.nodata_time = 0
		#Initialize sounds
		self.callouts = sounds.init_callouts(True)
		#Dynamic variable for testing
		self.dynamic_value = 0
		self.dynamic_step = 1
		
		#self.glass.__init__(self)
		
	
	def setup_GlassServer(self):
		self.glass = GlassServer.Glass_Server_c(self)
		self.glass.start()
		
	def setup_Client(self, left_screen, right_screen):
		self.right_screen = right_screen
		self.left_screen = left_screen
		import GlassClient
		self.client = GlassClient.client('127.0.0.1', config.server_port)
		self.client.connect()
		
		
	def read_Client(self):
		o = self.client.get_data(self.right_screen, self.left_screen, self.FMS)
		if 'FMS' in o:
			start = o.find("FMS") + 7
			output = o[start:]
			#print "%r" %output
			#print len(output)
		
			self.FMS.display.line_list = pickle.loads(output)
	def quit(self):
		self.quit_flag = True
		
	def setup_SimConnect(self, FSX_version):
		self.s = SimConnect('RJGlass', FSX_version, True)
		self.s.connect(config.addr, config.port, True)
		#Add definition's
		self.s.definition_0 = self.s.create_DataDefinition(2)
		#Data definition ID 2, is the high priority data, that needs to have no delay.
		self.s.definition_0.add("Airspeed Indicated", "knots", FLOAT32, self.airspeed.IAS)
		self.s.definition_0.add("GROUND VELOCITY", "knots", FLOAT32, self.airspeed.GS)
		
		self.s.definition_0.add("Heading Indicator", "degrees", FLOAT32, self.HSI.Mag_Heading)
		self.s.definition_0.add("MAGVAR", "degrees", FLOAT32, self.HSI.Mag_Variation)
		self.s.definition_0.add("Attitude Indicator Pitch Degrees", "degrees", FLOAT32, self.attitude.pitch)		self.s.definition_0.add("Attitude Indicator Bank Degrees", "degrees", FLOAT32, self.attitude.bank)
		self.s.definition_0.add("Vertical Speed", "ft/min", INT32, self.VSI)
		self.s.definition_0.add("Plane Latitude", "radians", FLOAT32, self.Latitude)
		self.s.definition_0.add("Plane Longitude", "radians", FLOAT32, self.Longitude)
		self.s.definition_0.add("Radio Height", "feet", INT32, self.altimeter.absolute)
		#self.s.definition_0.add("Kohlsman Setting HG", "inHG", FLOAT32, self.altimeter.pressure_HG)
		self.s.definition_0.add("Indicated Altitude", "feet", INT32, self.altimeter.indicated)
		self.s.definition_0.add("Airspeed Mach", "mach", FLOAT32, self.airspeed.Mach)
		#Flight Director
		#self.s.definition_0.add("AUTOPILOT FLIGHT DIRECTOR ACTIVE","", INT32, self.attitude.FD_active)
		#self.s.definition_0.add("AUTOPILOT FLIGHT DIRECTOR PITCH","degrees", FLOAT32, self.attitude.FD_pitch)
		#self.s.definition_0.add("AUTOPILOT FLIGHT DIRECTOR BANK","degrees", FLOAT32, self.attitude.FD_bank)
		#Autopilot
		#self.s.definition_0.add("AUTOPILOT ALTITUDE LOCK VAR","feet", INT32, self.altimeter.bug)
		self.s.definition_0.add("AUTOPILOT AIRSPEED HOLD VAR","knots", INT32, self.airspeed.bug)
		#Position of Flight controls
		self.s.definition_0.add("AILERON POSITION", "", FLOAT32, self.aileron_pos)
		self.s.definition_0.add("ELEVATOR TRIM PCT", "", FLOAT32, self.trim.Elevator, lambda x:(x+1)*7.5)
		self.s.definition_0.add("AILERON TRIM PCT", "", FLOAT32, self.trim.Aileron)
		self.s.definition_0.add("RUDDER TRIM PCT", "", FLOAT32, self.trim.Rudder)
		
		#self.s.definition_0.add("AUTOPILOT HEADING LOCK DIR","degrees", INT32, self.HSI.Heading_Bug)
		#Nav1 data
		self.s.definition_0.add("Nav OBS:1", "degrees", INT32, self.NAV.VOR1.OBS)
		self.s.definition_0.add("Nav Radial:1", "degrees", FLOAT32, self.NAV.VOR1.radial)
		self.s.definition_0.add("Nav CDI:1", "number", INT32, self.NAV.VOR1.CDI)
		self.s.definition_0.add("Nav GSI:1", "number", INT32, self.NAV.VOR1.GSI)
		self.s.definition_0.add("Nav has Nav:1", "bool", INT32, self.NAV.VOR1.hasNav)
		self.s.definition_0.add("Nav has Localizer:1", "bool", INT32, self.NAV.VOR1.hasLoc)
		self.s.definition_0.add("Nav has Glide Slope:1", "bool", INT32, self.NAV.VOR1.hasGS)
		self.s.definition_0.add("Nav DME:1", "Nautical Miles", FLOAT32, self.NAV.VOR1.DME)
		self.s.definition_0.add("NAV TOFROM:1", "Enum", INT32, self.NAV.VOR1.ToFrom)
		self.s.definition_0.add("Nav Ident:1", "", STRING8, self.NAV.VOR1.ID)
		#Nav2 data
		self.s.definition_0.add("Nav OBS:2", "degrees", INT32, self.NAV.VOR2.OBS)
		self.s.definition_0.add("Nav Radial:2", "degrees", FLOAT32, self.NAV.VOR2.radial)
		self.s.definition_0.add("Nav CDI:2", "number", INT32, self.NAV.VOR2.CDI)
		self.s.definition_0.add("Nav GSI:2", "number", INT32, self.NAV.VOR2.GSI)
		self.s.definition_0.add("Nav has Nav:2", "bool", INT32, self.NAV.VOR2.hasNav)
		self.s.definition_0.add("Nav has Localizer:2", "bool", INT32, self.NAV.VOR2.hasLoc)
		self.s.definition_0.add("Nav has Glide Slope:2", "bool", INT32, self.NAV.VOR2.hasGS)
		self.s.definition_0.add("Nav DME:2", "Nautical Miles", FLOAT32, self.NAV.VOR2.DME)
		self.s.definition_0.add("NAV TOFROM:2", "Enum", INT32, self.NAV.VOR2.ToFrom)
		self.s.definition_0.add("Nav Ident:2", "", STRING8, self.NAV.VOR2.ID)
		#ADF
		self.s.definition_0.add("ADF Radial:1", "degrees", INT32, self.NAV.ADF1.radial)
		self.s.definition_0.add("ADF Radial:2", "degrees", INT32, self.NAV.ADF2.radial)
		self.s.definition_0.add("ADF Signal:1", "number", INT32, self.NAV.ADF1.hasNav)
		self.s.definition_0.add("ADF Signal:2", "number", INT32, self.NAV.ADF2.hasNav)
		
		#Engine Data
		#Throttle
		self.s.definition_0.add("GENERAL ENG THROTTLE LEVER POSITION:1","percent",FLOAT32, self.Eng_1.Throttle)
		self.s.definition_0.add("GENERAL ENG THROTTLE LEVER POSITION:2","percent",FLOAT32, self.Eng_2.Throttle)
		
		#N1
		self.s.definition_0.add("TURB ENG N1:1", "percent", FLOAT32, self.Eng_1.N1)
		self.s.definition_0.add("TURB ENG N1:2", "percent", FLOAT32, self.Eng_2.N1)
		#ITT
		self.s.definition_0.add("TURB ENG ITT:1", "celsius", INT32, self.Eng_1.ITT)
		self.s.definition_0.add("TURB ENG ITT:2", "celsius", INT32, self.Eng_2.ITT)
		#N2
		self.s.definition_0.add("TURB ENG N2:1", "percent", FLOAT32, self.Eng_1.N2)
		self.s.definition_0.add("TURB ENG N2:2", "percent", FLOAT32, self.Eng_2.N2)
		#FUEL FLOW
		self.s.definition_0.add("TURB ENG FUEL FLOW PPH:1", "POUNDS PER HOUR", INT32, self.Eng_1.Fuel_Flow)
		self.s.definition_0.add("TURB ENG FUEL FLOW PPH:2", "POUNDS PER HOUR", INT32, self.Eng_2.Fuel_Flow)
		#Lbs of Thrust
		self.s.definition_0.add("TURB ENG JET THRUST:1","POUNDS",INT32,self.Eng_1.Thrust)
		self.s.definition_0.add("TURB ENG JET THRUST:2","POUNDS",INT32,self.Eng_2.Thrust)
		
		#Eng Oil Temp
		self.s.definition_0.add("ENG OIL TEMPERATURE:1", "celsius", INT32, self.Eng_1.Oil_Temp)
		self.s.definition_0.add("ENG OIL TEMPERATURE:2", "celsius", INT32, self.Eng_2.Oil_Temp)
		#Eng Oil Pressure
		self.s.definition_0.add("ENG OIL PRESSURE:1", "PSI", INT32, self.Eng_1.Oil_Pressure)
		self.s.definition_0.add("ENG OIL PRESSURE:2", "PSI", INT32, self.Eng_2.Oil_Pressure)
		#FAN Vibration
		self.s.definition_0.add("TURB ENG VIBRATION:1", "", FLOAT32, self.Eng_1.Fan_Vibration)
		self.s.definition_0.add("TURB ENG VIBRATION:2", "", FLOAT32, self.Eng_2.Fan_Vibration)
		#APU RPM
		self.s.definition_0.add("APU PCT RPM", "", FLOAT32, self.APU.RPM, lambda x:x*100)
		#On the Ground True/ False
		self.s.definition_0.add("SIM ON GROUND", "", INT32, self.onground)
		#Ground Heading (used for green circle on HSI and moving map)
		self.s.definition_0.add("GPS GROUND MAGNETIC TRACK", "degrees", FLOAT32, self.HSI.Mag_Track)
		#Setup to be read once. Will be repeated after every incoming packet.
		# Note: This was the only way I could get the network delay down low enough.
		self.s.definition_0.add("TURN COORDINATOR BALL", "Position 128", INT32,  self.attitude.turn_coord)
		self.s.definition_0.add("AILERON POSITION","",FLOAT32, self.TEST4)
		
		#Non critical data, can be updates ever second or so.
		#self.s.definition_1 = self.s.create_DataDefinition(7)
		self.s.definition_0.add("TOTAL WEIGHT","POUNDS",INT32, self.total_weight)
		#Fuel Quantity
		self.s.definition_0.add("FUEL TANK CENTER QUANTITY","GALLONS",FLOAT32, self.fuel.center.gal)
		self.s.definition_0.add("FUEL TANK LEFT MAIN QUANTITY","GALLONS",FLOAT32, self.fuel.left.gal)
		self.s.definition_0.add("FUEL TANK RIGHT MAIN QUANTITY","GALLONS",FLOAT32, self.fuel.right.gal)
		#Brakes
		self.s.definition_0.add("BRAKE LEFT POSITION","",FLOAT32, self.brakes.Left_Pedal)
		self.s.definition_0.add("BRAKE RIGHT POSITION","",FLOAT32, self.brakes.Right_Pedal)
		self.s.definition_0.add("BRAKE PARKING POSITION","",FLOAT32, self.brakes.Parking_Brake)
		
		#Flap handle
		self.s.definition_0.add("FLAPS HANDLE INDEX", "", INT32, self.flaps.handle)
		self.s.definition_0.add("TRAILING EDGE FLAPS LEFT PERCENT", "", FLOAT32, self.flaps.pos)
		self.s.definition_0.add("GEAR HANDLE POSITION","", INT32, self.gear.handle)
		#Markers
		self.s.definition_0.add("MARKER BEACON STATE", "", INT32, self.attitude.marker)
		#Gear
		self.s.definition_0.add("GEAR CENTER POSITION","percent over 100", FLOAT32, self.gear.Nose.position)
		self.s.definition_0.add("GEAR LEFT POSITION","percent over 100", FLOAT32, self.gear.Left.position)
		self.s.definition_0.add("GEAR RIGHT POSITION","percent over 100", FLOAT32, self.gear.Right.position)
		#Outside Temp
		self.s.definition_0.add("AMBIENT TEMPERATURE","celsius",FLOAT32, self.OAT)
		
		
		self.s.definition_0.request(4, DataDefinition.USER, DataDefinition.ONCE, interval = 0, flag = 0)
		#Request data every second
		#self.s.definition_1.request(5, DataDefinition.USER, DataDefinition.SECOND, interval = 1)
		
		self.sevent = SimConnect('RJGlass Event', FSX_version, True)
		self.sevent.connect(config.addr, config.port, False)		
		#Create notification group
		self.sevent.eventlist = self.sevent.create_EventList()
		self.sevent.eventlist.add("HEADING_BUG_SET", self.HSI.Heading_Bug)
		self.sevent.eventlist.add("AILERON_SET", self.AP.aileron_pos)
		self.sevent.eventlist.add("ELEVATOR_TRIM_SET", self.AP.elevtrim_pos)
		self.sevent.eventlist.add("KOHLSMAN_SET", self.altimeter.Kohlsmanx16)
		#self.sevent.group1.add("AP_ALT_VAR_SET_ENGLISH", self.TEST2)
		#self.sevent.group1.add("AP_ALT_VAR_INC", self.TEST2)
		#self.s.group1.set_priority(10)
		#time.sleep(10)
		
	def kill_SimConnect(self):
		self.s.client.go = False
		self.sevent.client.go = False
		
	def decode_define_id(self):
		#Note this just checks for define_id 2, to see if data recieved.
		define_id = self.s.receive()
		b = False
		#print define_id
		length = len(define_id)
		#if length > 0:  #This means data was recieved
		#	print define_id
		
		if self.s.definition_0.id in define_id: #Define ID is high priority data, if received then compute, and request another.
			
			#start_time = 0.0
			self.s.definition_0.request(4, DataDefinition.USER, DataDefinition.ONCE, interval = 0, flag = 0)
			self.comp() # Main computation loop
			self.nodata = False #Rest no data boolean	
			b = True
		#if self.s.definition_1.id in define_id: (Not used anymore)
			#self.comp_second()
		return b
	
	def read_FSX(self):
		

		if self.decode_define_id() == False: #If no define_id 2 (high priority data) recieved then
		#Data not recieved, keep trying to resent request every 2 seconds.
			diff = globaltime.value - self.nodata_time
			if diff > 2.0: #If no data for 2 seconds.
			#Request data
				self.nodata = True
				#Request more data from FSX (This was causing multiple requests removed for now)
				#self.s.definition_0.request(4, DataDefinition.USER, DataDefinition.ONCE, interval = 0, flag = 0)
				self.nodata_time +=2 #Reset timer so request again in 2 seconds.
		else:
			self.nodata_time = globaltime.value
			self.nodata = False
			
	def comp_frame_time(self, i):
		if self.count2 >= i:
			t = globaltime.value
			self.frame_time = (t - self.clock) / self.count2
			self.clock = t
			self.count2 = 0
		#print self.frame_time

		else:
			self.count2+=1

	def get_PFD_data(self):
		return pickle.dumps(self.PFD_pickle, -1)

		
	def comp(self, test=False):
		#Test is true, if RJGlass is in test mode.
		self.global_time = globaltime.value
		#Computer delta_t = Time between last comp and this one
		delta_t = self.global_time - self.prev_time
		if delta_t > 0.1: delta_t = 0.1 #Limit to .1 sec (incase of hickup)
		self.prev_time = self.global_time
		
		#Computation section, main one for data that is updated every frame.
		#self.count+=1
		self.comp_time+= delta_t

		if self.comp_time > 1.0:
			self.comp_time -= 1.0
			#Do low priority stuff
			self.brakes.comp(self)
			self.comp_second()
			
		self.FMS.check_buttons()
		self.airspeed.comp()
		
		self.AP.comp(self)
		self.Eng_1.comp()
		self.Eng_2.comp()
		self.flaps.comp()
		self.gear.comp()
		self.fuel.comp()
		self.APU.comp(delta_t,self.global_time)
		
		self.trim.comp(self.onground)
		
		EICAS_comp(self)
		self.declutter.comp(self.attitude.pitch.value, self.attitude.bank.value)
		if self.altimeter.indicated.value <-1000: self.altimeter.indicated.value = -1000
		#self.altimeter.calc_indicated()
		#Radial calc, to bearing
		#self.VOR1.bearing = Turn_180(self.VOR1.radial)
		self.attitude.GS = self.NAV.active.GSI.value
		#self.attitude.GS = self.VOR1.GSI
		#IAS Acceleration section
		self.comp_frame_time(20)
		self.airspeed.comp_IAS_accel(self.airspeed, self.frame_time)
		
		#Check to see if IAS speed trend (Pink line) visible
		if self.airspeed.trend_visible: #If on check if speed <105kts
			if self.airspeed.IAS.value <105:
				self.airspeed.trend_visible = False
		else: #If off check for H>20ft
			if self.altimeter.absolute.adjusted > 20:
				self.airspeed.trend_visible = True
		
		self.HSI.True_Heading = Check_360(self.HSI.Mag_Heading.value + self.HSI.Mag_Variation.value)
		#self.HSI.True_Heading = Check_360(self.HSI.Mag_Heading.value + 0)
		#print "RA ", self.altimeter.absolute.value
		self.altimeter.absolute.adjusted = self.altimeter.absolute.value - 7
		#Mach visible
		if self.airspeed.Mach.value < 0.4:
			self.airspeed.Mach.active = False
		elif self.airspeed.Mach.value >=0.45:
			self.airspeed.Mach.active = True
		#Check for altitude callouts
		#if self.altimeter.MDA.changed or self.altimeter.DH.changed: #If they changed then update minimums
		if self.altimeter.absolute.adjusted < 2500: #If under 2500 AGL then check altitude callouts
			self.callouts.update_minimums(self.altimeter.MDA, self.altimeter.DH, self.altimeter.absolute.adjusted, self.altimeter.indicated.value)
			self.callouts.check(self.altimeter.absolute.adjusted, self.altimeter.indicated.value)
		
		#Check for change in outgoing data to FSX. (Event_obj)
		if test == False:
			self.sevent.eventlist.send_updates()
		#self.sevent.group1.cycle()
		#print self.HSI.Mag_Variation.value, self.HSI.True_Heading
		
	def comp_second(self):
		#Computation section for low prority data that needs to be checked ever second.
		temp = self.flaps.handle.value
		if temp <=5: 
			self.airspeed.maxspeed = config.VNE_flaps[temp]
			self.airspeed.minspeed = config.VS_flaps[temp] * 1.06
			self.airspeed.lowspeed = config.VS_flaps[temp] * 1.265
			#print self.airspeed.maxspeed, self.airspeed.minspeed
		if self.gear.handle.value:
				if self.airspeed.maxspeed> config.Gear_speed_limit:
					self.airspeed.maxspeed = config.Gear_speed_limit
		#Total distance traveled used by ND.
		self.ND.dis_traveled.calc(self.Latitude.value, self.Longitude.value)
		#print self.ND.dis_traveled.total
	
	def get_mode_func(self, mode, right_screen, left_screen):
		if mode==config.TEST: 
			mode_func = self.test
			self.setup_GlassServer()
		elif mode==config.FSXSP0:
			mode_func = self.read_FSX
			self.setup_SimConnect(mode)
		elif mode==config.FSXSP1:
			mode_func = self.read_FSX
			self.setup_SimConnect(mode)
		elif mode==config.FSXSP2: 
			mode_func = self.read_FSX
			self.setup_SimConnect(mode)
		elif mode==config.ESP: #Not tested yet
			mode_func = self.read_FSX
			self.setup_SimConnect(mode)
		elif mode==config.CLIENT:
			mode_func = self.read_Client
			self.setup_Client(left_screen, right_screen)
		else:
			print "ERROR: Mode in config file is not defined"
		return mode_func
			
	def testing_key(self):
		#self.Latitude.value = math.radians(33.62)
		#self.Longitude.value = math.radians(-84.43)
		#print "LAT LONG"
		#print self.Latitude.value, self.Longitude.value
		#print math.degrees(self.Latitude.value), math.degrees(self.Longitude.value)
		#self.TEST.send_value = 100
		#self.AP.turnon()
		self.Longitude.value +=math.radians(0.01)
		self.flaps.pos.value = 0.0
		self.APU.RPM.value = 0
	def dynamic_inc(self):
		self.dynamic_value+=self.dynamic_step
		print self.dynamic_value
	def dynamic_dec(self):
		self.dynamic_value-=self.dynamic_step
		print self.dynamic_value
		
	def test(self):

		#time.sleep(0.01)
		self.attitude.bank.value += 0.005
		self.attitude.pitch.value =0.0
		self.gear.Left.position.value = 0.0
		self.gear.Nose.position.value = 0.0
		self.gear.Right.position.value = 0.0
		#print pickle.dumps(self.attitude)
		#self.Longitude.value +=0.01*6.28/180.0
		#self.attitude.pitch = 20.0
		self.fuel.left.gal.value -=0.1
		self.comp(True) #Set true to tell self.comp, RJGlass is in test mode.
		#self.comp_frame_time(20)
		#self.NAV.VOR1.CDI.value = 30
		#self.VOR1.active = False
		#self.HSI.Mag_Heading.value = Check_360(self.HSI.Mag_Heading.value + 0.1)
		self.HSI.Mag_Heading.value =0.0
		#self.airspeed.IAS.value -= 0.03
		self.VSI.value = 1000
		self.Eng_1.N2.value = 65.1
		self.Eng_2.N2.value = 65.5
		#self.flaps.pos.value += 0.002
		#self.flaps.pos.value = 0.0
		#self.attitude.FD_pitch +=0.07
		#self.attitude.FD_bank.value =45.00
		#self.attitude.GS +=1
		#self.altimeter.DH.bug = 320
		#self.HSI.Mag_Heading = Check_360(self.HSI.Mag_Heading-0.1)
		#self.HSI.Heading_Bug.value  = Check_360(254)
		self.NAV.VOR1.OBS.value = 112
#		self.altimeter.absolute.value = 10
		if self.count >=30:
			#self.Latitude.value -=math.radians(0.0002)
			self.altimeter.indicated.value = self.altimeter.indicated.value + 7
			#self.altimeter.absolute.value -=1
			#self.NAV.VOR1.CDI.value +=1
			#self.NAV.VOR1.DME.value = self.NAV.VOR1.CDI.value
			#self.ND.range.down()
			#self.VertSpeed +=10
			self.NAV.VOR1.hasGS.value = False
			#self.NAV.VOR1.hasLoc.value = True
			#self.VOR1.ToFrom = False
			#time.sleep(10)
			self.count =0
			#self.comp_second() (Note: Now done within self.comp())
		#else:
		#	self.HSI.Heading_Bug+=1
	#	self.altimeter.absolute = 200
	#		self.count =0
		self.count +=1 
	def server_request(self, d):
		if d.strip("PFD"):
			return self.PFD_pickle.pickle_string()

