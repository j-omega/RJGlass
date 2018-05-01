#!/usr/bin/env python
# ----------------------------------------------------------
# PFDND_data MODULE for GlassCockpit procject RJGlass
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



from guage import *
from PySimConnect import *
import formula
import pickle
import GlassServer
import FMS_control


class PFD_pickle_c(object):
	def __init__(self, aircraft):
		self.attitude = aircraft.attitude
		
	def pickle_string(self):
		return pickle.dumps(self, -1)
	
class ND_c(object): #Class the handles the Nav Display (ND)
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
		#print self.total, d
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

		
class MDA_DH_c(object): #The class for MDA and DH (They have very similar functions)
	def __init__(self, step):
		self.bug = 200
		self.visible = False
		self.selected = False
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
			
			
class altimeter_c(object):
	
	def __init__(self):
		self.HG = 0
		self.HPA = 1
		self.pressure_unit = self.HG
		self.indicated = data_obj(20)
		self.pressure_HG = 29.92 #Kohlsman HG Altimeter Setting
		self.pressure_HPA = 1013
		self.setting = 29.92
		self.absolute = data_obj(20) #Absolute / Radar Altitude (Altitude Above Ground)
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
		
class HSI_c(object):
	def __init__(self):
		#Constants
		self.NADA =0
		self.VOR = 1
		self.ADF = 2
		self.FMS = 3
		#Variables
		self.Mag_Heading = data_obj(123.5)
		self.True_Heading = 0.0
		self.Mag_Variation = data_obj(0)
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
		self.Heading_Bug.update = True
		self.Heading_Bug_Timer = globaltime.value + 5
		
	def dec_Heading_Bug(self):
		self.Heading_Bug.value = Check_360(self.Heading_Bug.value -1)
		self.Heading_Bug.update = True
		self.Heading_Bug_Timer = globaltime.value + 5

class VOR_c(object):
			
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
class NAV_c(object):
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
class ADF_c(object):
	def __init__(self, name):
		self.radial = data_obj(100)
		self.active = data_obj(True)
		self.hasNav = data_obj(-1)
		self.name = name

class attitude_c(object):
	
	def __init__(self):
		self.pitch = data_obj(10.0)
		self.bank = data_obj(10.0)
		self.FD_active = data_obj(0)
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




		
#class gear_c(object):
#	def __init__(self):
#		self.handle = data_obj(0) #Either 0 or -1 

class V_speed_c(object):
	
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

class declutter_c(object):
	def __init__(self):
		self.active = False
		
	def comp(self, pitch, bank): #Declutter active when pitch >=30 or <= -20, bank >= 65 degrees
		if (pitch >= 20.0) | (pitch <= -30.0): #Pitch is reversed from FSX
			self.active = True
		elif (abs(bank) >= 65.0):
			self.active = True
		else:
			self.active = False
			

class airspeed_c(object):
	
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
		self.GS = data_obj(0.0)
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