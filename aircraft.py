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

class data(object):

	
	def __init__(self, PFD):
		self.global_time = 0.0 #Used for timing reasons. 
		self.count = 0
		self.quit_flag = False #If True then RJGlass will exit
		self.attitude = attitude_c()
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
		self.gear = gear_c()
		self.onground = data_obj(0)
		
		self.HSI = HSI_c()
		self.NAV = NAV_c()
	#	self.ADF1 = ADF_c("ADF1")
	#	self.ADF2 = ADF_c("ADF2")
		self.ND = ND_c()
		self.VSI = data_obj(-800)
		self.TEST = event_obj(32000)
		self.TEST4 = data_obj(100)
		self.TEST2 = event_obj(100)
		#self.LatLong = (math.radians(41.9217),math.radians(-84.0825))
		self.Latitude = data_obj(math.radians(41.9217))
		self.Longitude = data_obj(math.radians(-84.0825))
		
#		self.LatLong = (0.73675821079214898, -1.4550227732038261)
		#Frame Timer Variables
		self.clock = time.time() 
		
		self.count2 = 0 #counter used to determine clock cycle
		self.frame_time = 0.01 #Time between frames. 1 / frame_time = FPS (frames per second)
		self.nodata = False
		#Initialize sounds
		self.callouts = sounds.init_callouts(True)
		
	def quit(self):
		self.quit_flag = True
		
	def setup_SimConnect(self, FSX_version):
		self.s = SimConnect('RJGlass', FSX_version, True)
		self.s.connect(config.addr, config.port, True)
		#Add definition's
		self.s.definition_0 = self.s.create_DataDefinition(2)
		#Data definition ID 2, is the high priority data, that needs to have no delay.
		self.s.definition_0.add("Airspeed Indicated", "knots", FLOAT32, self.airspeed.IAS)
		#self.s.definition_0.add("Indicated Altitude", "feet", INT32, self.altimeter.indicated)
		self.s.definition_0.add("Heading Indicator", "degrees", FLOAT32, self.HSI.Mag_Heading)
		self.s.definition_0.add("Attitude Indicator Pitch Degrees", "degrees", FLOAT32, self.attitude.pitch)
		self.s.definition_0.add("Attitude Indicator Bank Degrees", "degrees", FLOAT32, self.attitude.bank)
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
		self.s.definition_0.add("ELEVATOR TRIM INDICATOR", "", FLOAT32, self.elev_trim)
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
		#Flap handle
		self.s.definition_0.add("FLAPS HANDLE INDEX", "", INT32, self.flaps.handle)
		self.s.definition_0.add("GEAR HANDLE POSITION","", INT32, self.gear.handle)
		#Markers
		self.s.definition_0.add("MARKER BEACON STATE", "", INT32, self.attitude.marker)
		
		self.s.definition_0.request(4, DataDefinition.USER, DataDefinition.ONCE, interval = 0, flag = 0)
		#Request data every second
		#self.s.definition_1.request(5, DataDefinition.USER, DataDefinition.SECOND, interval = 1)
		
		self.sevent = SimConnect('RJGlass Event', FSX_version, True)
		self.sevent.connect(config.addr, config.port, False)		
		#Create notification group
		self.sevent.eventlist = self.sevent.create_EventList()
		#self.sevent.eventlist.add("HEADING_BUG_SET", self.HSI.Heading_Bug)
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
		#if self.s.definition_1.id in define_id:
			self.comp_second()
		return b
	
	def read_FSX(self):
		
		self.nodata = True
		if self.decode_define_id() == False: #If no define_id 2 (high priority data) recieved then
		#Data not recieved, keep trying for 0.5 seconds then continue with nodata flag set.
			start_time = time.time() #Try for 0.5 seconds
			while (time.time() - start_time) < 0.5:
				if self.decode_define_id(): 
					start_time =0.0 #Data recieved, this will make while loop exit
			#If data recieved in first if statement, then just exit loop
			
	def comp_frame_time(self, i):
		if self.count2 >= i:
			t = globaltime.value
			self.frame_time = (t - self.clock) / self.count2
			self.clock = t
			self.count2 =0
		#print self.frame_time

		else:
			self.count2+=1


		
	def comp(self):
		#Computation section, main one for data that is updated every frame.
		self.airspeed.comp()
		self.global_time = globaltime.value
		self.AP.comp(self)
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
		
		self.HSI.True_Heading = Check_360(self.HSI.Mag_Heading.value + self.HSI.Mag_Variation)
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
		#self.sevent.eventlist.send_updates()
		#self.sevent.group1.cycle()
		
	def comp_second(self):
		#Computation section for data that is updates every second.
		#print "Flap position", self.TEST_INT.value
		#Flaps
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
	
	def get_mode_func(self, mode):
		if mode==config.TEST: mode_func = self.test
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
		self.AP.turnon()
	def test(self):

		time.sleep(0.01)
		self.attitude.bank.value = 0.0
		self.attitude.pitch.value =0.0
		
		#self.attitude.pitch = 20.0
		self.comp()
		#self.comp_frame_time(20)
		#self.NAV.VOR1.CDI.value = 30
		#self.VOR1.active = False
		self.HSI.Mag_Heading.value =273
		#self.HSI.Mag_Heading =1
		#self.airspeed.IAS.value -= 0.03
		self.VSI.value = 1000
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
			#self.altimeter.value = self.altimeter.value + 7
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
			self.comp_second()
		#else:
		#	self.HSI.Heading_Bug+=1
	#	self.altimeter.absolute = 200
	#		self.count =0
		self.count +=1 
		
	
class ND_c(data): #Class the handles the Nav Display (ND)
	def __init__(self):
		self.range = range_c()
		self.dis_traveled = dis_travel_c()
		
class dis_travel_c(ND_c):
	def __init__(self):
		self.prev_lat = 1.0 #Used to caclulate total distance traveled
		self.prev_long = 1.0
		self.total = 0.0 #Total distance traveled
		self.increment = 0.0
	def calc(self, lat, long):
		#print lat,long, self.prev_lat, self.prev_long
		d = formula.dist_latlong_nm((lat,long),(self.prev_lat,self.prev_long))
		if d>0.005: #Used if isn't moving plane doesn't slowly move. Due to calc not being 0.0
			self.total +=d
							
		self.prev_lat = lat
		self.prev_long = long
		self.increment = d
		
	def reset(self):
		self.total = 0.0
		self.increment = 0.0
		
		
class range_c(ND_c):
	def __init__(self):
		self.index = 3
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
	def __init__(self, step):
		self.bug = 200
		self.visible = True
		self.selected = True
		self.notify = False #On if MDA_DH notification is on
		self.flash = 0 #Int used for flashing of notifier (MDA use only)
		self.frame_count = 0 #Used for flash delay of MDA notifier
		self.increment = step #The lowest increment for MDA or DH
		self.changed = True
		
	def cycle_visible(self):
		self.changed = True
		if self.visible:
			self.visible = False
		else:
			self.visible = True
			
	def bug_increase(self):
		if self.visible: #Must be visible to change value
			self.bug += self.increment
			self.changed = True
	def bug_decrease(self):
		self.changed = True
		if self.visible: #Must be visible to change value
			self.bug -= self.increment
			if self.bug <0:
				self.bug = 0
			
			
class altimeter_c(data):
	
	def __init__(self):
		self.HG = 0
		self.HPA = 1
		self.pressure_unit = self.HG
		self.indicated = data_obj(620)
		self.pressure_HG = 29.92 #Kohlsman HG Altimeter Setting
		self.pressure_HPA = 1013
		self.setting = 29.92
		self.absolute = data_obj(620) #Absolute / Radar Altitude (Altitude Above Ground)
		self.MDA = MDA_DH_c(10) #First number is ID needs to be 0 for MDA
		self.DH = MDA_DH_c(1) #ID 1 for DH
		self.bug = data_obj(3000)
		self.Kohlsmanx16 = event_obj(0)
	
	def convert_to_HPA(self):
		self.pressure_HPA = int(round(1013.2 / 29.92 * self.pressure_HG, 0))
		#Used to send out to FSX.
		self.Kohlsmanx16.value = int(round(1013.2 / 29.92 * self.pressure_HG * 16, 0))
		self.Kohlsmanx16.update = True
		self.setting = self.pressure_HG

	def convert_to_HG(self):
		#temp = 29.92 / 1013.0 * self.pressure_HPA
		self.pressure_HG = round(29.92 / 1013.2 * self.pressure_HPA, 2)
		self.setting = self.pressure_HPA #Since converting to HG HPA is valid setting
		self.Kohlsmanx16.value = int(round(self.pressure_HPA * 16, 0))
		self.Kohlsmanx16.update = True
	def reset_setting(self):
		#Reset it to 29.92 / 1013
		self.pressure_HG = 29.92
		self.pressure_HPA = 1013
		self.Kohlsmanx16.value = int(round(1013 * 16,0))
		self.Kohlsmanx16.update = True
		if self.pressure_unit == self.HG:
			self.setting = self.pressure_HG
		else:
			self.setting = self.pressure_HPA
	def  inc_setting(self):
		#increase the Kohlsman Pressure
		if self.pressure_unit == self.HG:
			self.pressure_HG += 0.01
			self.convert_to_HPA()
		else:
			self.pressure_HPA += 1
			self.convert_to_HG()
			
	def  dec_setting(self):
		#Decrease the Kohlsman Pressure
		if self.pressure_unit == self.HG:
			self.pressure_HG -= 0.01
			self.convert_to_HPA()
		else:
			self.pressure_HPA -= 1
			self.convert_to_HG()
	def change_unit(self):
		if self.pressure_unit == self.HG:
			round(self.pressure_HPA,0) #Convert it to .0, to be consistent.
			self.pressure_unit = self.HPA
			self.setting = self.pressure_HPA
			self.convert_to_HG() #Used to update everything, and send data to FSX
		else:
			round(self.pressure_HG, 2) #Round to 2 deciman, be consistent.
			self.pressure_unit = self.HG
			self.setting = self.pressure_HG
			self.convert_to_HPA() #Used to update everything, and send data to FSX
	def bug_inc(self):
		self.bug.value += 100
		if self.bug.value >60000: self.bug.value = 60000
		
	def bug_dec(self):
		self.bug.value -=100
		if self.bug.value < 0: self.bug.value = 0
		
class HSI_c(data):
	def __init__(self):
		#Constants
		self.NADA =0
		self.VOR = 1
		self.ADF = 2
		self.FMS = 3
		#Variables
		self.Mag_Heading = data_obj(123.5)
		self.True_Heading = 0.0
		self.Mag_Variation = 0.0
		self.Mag_Track= data_obj(130.0)
		self.Heading_Bug = event_obj(20)
		self.Heading_Bug_Timer = 0 #Used as timer for drawing heading bug when its value changes
		self.Heading_Bug_prev = 20
		self.Bearing1 = self.ADF #Will either be FMS, VOR or ADF
		self.Bearing2 = self.VOR

	def cycle_Bearing1(self):
		self.Bearing1+=1
		if self.Bearing1 > self.ADF:
			self.Bearing1 = self.NADA

	def cycle_Bearing2(self):
		self.Bearing2 +=1
		if self.Bearing2 > self.ADF:
			self.Bearing2 = self.NADA

	def inc_Heading_Bug(self):
		self.Heading_Bug.value = Check_360(self.Heading_Bug.value +1)
		
	def dec_Heading_Bug(self):
		self.Heading_Bug.value = Check_360(self.Heading_Bug.value -1)
class VOR_c(data):
			
	def __init__(self, name):
		self.OBS = data_obj(330)
		self.CDI = data_obj(-27)
		self.GSI = data_obj(27)
		self.DME = data_obj(0.5)
		self.ID = data_obj("ATL")
		self.name = name
		self.hasNav = data_obj(-1) 
		self.hasGS = data_obj(0)
		self.hasLoc = data_obj(0)
		self.radial = data_obj(20)
		#self.radial = 200
		self.ToFrom = data_obj(2)
		self.ToFrom.TO = 1
		self.ToFrom.FROM = 2
		self.active = data_obj(-1)
class NAV_c(data):
	#Class for navaids, 1 and 2
	def cycle_Active_NAV(self): #Between VOR1 and VOR2 for now.
		if self.active == self.VOR1:
			self.active = self.VOR2
		else:
			self.active = self.VOR1
	def __init__(self):
		self.VOR1 = VOR_c("VOR1")
		self.VOR2 = VOR_c("VOR2")
		self.ADF1 = ADF_c("ADF1")
		self.ADF2 = ADF_c("ADF2")
		self.active = self.VOR1  #Make VOR1 active nav.
	#	self.VOR2.radial.value = 150
	#	self.VOR2.hasGS.value = -1
	#	self.VOR2.ID.value = "CVG"
class ADF_c(data):
	def __init__(self, name):
		self.radial = data_obj(100)
		self.active = data_obj(True)
		self.hasNav = data_obj(-1)
		self.name = name

class attitude_c(data):
	
	def __init__(self):
		self.pitch = data_obj(10.0)
		self.bank = data_obj(10.0)
		self.FD_active = data_obj(-1)
		self.FD_pitch = data_obj(10.0)
		self.FD_bank = data_obj(10.0)
#		self.GS = -127
		self.marker = marker_c()
		self.turn_coord = data_obj(0)
		
class marker_c(attitude_c):
		def __init__(self):
			#Constants
			self.OM = 1
			self.MM = 2
			self.IM = 3
			
			self.value = self.OM #Which marker is on
			self.count = 0

class flaps_c(data):
	
	def __init__(self):
		self.handle = data_obj(2)
		
class gear_c(data):
	def __init__(self):
		self.handle = data_obj(0) #Either 0 or -1 

class V_speed_c(data):
	
	def inc(self):
		self.value += 1
		if self.value > 350:
			self.value = 350
			
	def dec(self):
		self.value -= 1
		if self.value < 40:
			self.value = 40
	
	def onoff(self):
		if self.visible:
			self.visible= False
		else:
			self.visible = True
	
	def __init__(self, text, initvalue):
		self.value = initvalue
		self.visible = True
		self.text = text

class declutter_c(data):
	def __init__(self):
		self.active = False
		
	def comp(self, pitch, bank): #Declutter active when pitch >=30 or <= -20, bank >= 65 degrees
		if (pitch >= 20.0) | (pitch <= -30.0): #Pitch is reversed from FSX
			self.active = True
		elif (abs(bank) >= 65.0):
			self.active = True
		else:
			self.active = False
			

		
	

class airspeed_c(data):
	
	def set_disp(self, Vspeed):
		#This sets what is displayed below speed tape. (Goes blank after a few seconds)
		self.Vspeed_disp = Vspeed
		self.Vspeed_disp_timer = globaltime.value + 5 #5 seconds display
		
		
	def cycle_Vspeed_input(self):
		temp = self.Vspeed_input
		if temp == self.V1:
			out = self.VR
		elif temp == self.VR:
			out = self.V2
		else:
			out = self.V1
		self.Vspeed_input = out
		self.set_disp(out)
					
	def inc_Vspeed_input(self):
		self.Vspeed_input.inc()
		self.set_disp(self.Vspeed_input)
		
	def dec_Vspeed_input(self):
		self.Vspeed_input.dec()
		self.set_disp(self.Vspeed_input)
		
	def visible_Vspeed_input(self):
		self.Vspeed_input.onoff()
		self.set_disp(self.Vspeed_input)
		
	def inc_VT(self):
		self.VT.inc()
		self.set_disp(self.VT)
	def dec_VT(self):
		self.VT.dec()
		self.set_disp(self.VT)
		
	def visible_VT(self):
		self.VT.onoff()
		self.set_disp(self.VT)
	
	
	def __init__(self):
		self.IAS = data_obj(360.0) #self.IAS.value is value read from FSX
		self.IAS_guage = 360.0
		self.IAS_diff = 10.0 #Pink Line to show accel or decell
		self.trend_visible = False #Speed trend turns on  H> 20ft, turns off speed <105kts
		self.IAS_prev = self.IAS.value
		self.IAS_list = [0] * 40 # This is used to compute IAS accelertation for airspped tape
		self.TAS = 0.0
		self.Mach = data_obj(0.475)
		self.Mach.active = False
		self.GS = 0.0
		self.V1 = V_speed_c("V1 ", 135)
		self.V2 = V_speed_c("V2 ", 144)
		self.VR = V_speed_c("VR ", 137)
		self.VT = V_speed_c("VT ", 110)
		self.Vspeed_input = self.V1  #Currently selected one to be changed by knob
		self.Vspeed_disp = self.V1 #The one that is displayed below speed tape
		self.Vspeed_disp_timer = 0 #Used for delay of timer
		self.bug = data_obj(150)
		self.maxspeed = 260 #Never Exceed speed Red line
		self.minspeed = 220 #Stall speed
		self.lowspeed = 140
			
	def comp(self):
		#Comput the data for airspeed
		#self.IAS.
		if self.IAS.value <=40:
			self.IAS_guage = 40
		else: 
			self.IAS_guage = self.IAS.value

	def comp_IAS_accel(self, airspeed, frame_rate):
		#Computes forcastes IAS in 10 seconds for the IAS tape IAS_diff
		#Find difference between new_IAS and last reading
		diff = self.IAS.value - self.IAS_prev
		self.IAS_prev = self.IAS.value
		#Add diff reading to list pop oldest one
		self.IAS_list.append(diff)
		self.IAS_list.pop(0)
		a= self.IAS_list
		self.IAS_diff = (sum(a) / len(a)) / frame_rate * 10