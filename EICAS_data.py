#!/usr/bin/env python
# ----------------------------------------------------------
# EICAS_data MODULE for GlassCockpit procject RJGlass
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
import random
#This is code to import config file (config.py)
try:
	import config
except ImportError:
	# We're in a py2exe, so we'll append an element to the (one element) 
	# sys.path which points to Library.zip, to the directory that contains 
	# Library.zip, allowing us to import config.py
	# Adds one level up from the Library.zip directory to the path, so import will go forward
	sys.path.append(os.path.split(sys.path[0])[0])
	import config


class EICAS_pickle_c(object):
	def __init__(self, aircraft):
		#self.attitude = aircraft.attitude
		self.list = [aircraft.Eng_1, aircraft.Eng_2]
			
		#self.Eng_1 = aircraft.Eng_1
		#self.Eng_2 = aircraft.Eng_2
		
	#def pickle_string(self):
	#	return pickle.dumps(self, -1)
	
	
	def pickle_string(self):
		l = []
		for i in self.list:
			l.append(i.encode())
		return pickle.dumps(l, True)
	
	
class Engine_constants(object):
	def __init__(self):
		
		#N1 Overspeed
		self.N1_Overspeed = 98.6
		#N2 Overspeed
		self.N2_Overspeed = 99.3
		#ITT Overtemp
		self.ITT_OverTemp = 900
		#Oil Temp
		self.OilTemp_Red = 163
		self.OilTemp_Amber = 150
		#Oil Pressure
		self.OilPres_Red = 25
		self.OilPres_Amber = 115
		#Fan Vibraton
		self.FANVIB_Yellow = 2.4

class show_GEARFLAP_c(object):
		#Timer for flap and Gear guages.
		#--- If these conditions are met for 30 sec, flap and gear not displayed.
		#   1) Gear Up and Locked
		#   2) Flaps up
		#   3) Brake Temp Normal
		def __init__(self):
			self.show = True
			self.time = 0
			self.max_time = 30
			
		def comp(self, flaps, gear_up, brakes_normal, globaltime):
			
			if (flaps.pos.value == 0.0) & (gear_up== True) & (brakes_normal == True):
				if (globaltime - self.time) > self.max_time:
					self.show = False
			else:
				self.time = globaltime
				self.show = True
			
class showFANVIB_c(object):
		#Class determins if Vibration or OilPressure guages displayed.
	def __init__(self):
		self.show = False
		self.timer = 0
		
		
	def comp(self, Eng1, Eng2, onground, globaltime):
		#Uses Eng1 and Eng2 data to determine to show FanVIB or not.
		#Logic -- Fan Vibration appears if both engines have reached 55% N2 + 2 seconds, and oil pressure is above 24psi.
		#	Oil Pressure guage appears if low oil pressure in
		#	During single engine operation on ground shows oil guages, in air shows Fan Vibration.
		
		#Check oil pressure
		self.show = True #Assume not showing
		if onground:
			#If neither has low pressure and both running
			if (Eng1.lowOil_Pressure) | (Eng2.lowOil_Pressure) | (not Eng1.running) | (not Eng2.running):
				self.show = False
		else: #In the air
			if (Eng1.running) & (Eng1.lowOil_Pressure):
				self.show = False
			elif (Eng2.running) & (Eng2.lowOil_Pressure):
				self.show = False
			elif (not Eng1.running) & (not Eng2.running):
				self.show = False
					
		# Check for time delay of 2 seconds in all cases
		if self.show == False:
			self.timer = globaltime #Reset 2 second timer. If VIB not shown
		else: #check for 2 second delay
			if (globaltime - self.timer) < 2.0:
				self.show = False 
			
class Trim_c(object):
	def __init__(self):
		self.Aileron = data_obj(0)
		self.Elevator = data_obj(0)
		#self.Elevator_disp = 0
		self.Rudder = data_obj(0)
		self.needles_green = False
		self.elevator_green = False
		
	def comp(self, onground):
		#Check to see if Elevator is within Green 3 - 9
		if 3 <= self.Elevator.value <= 9:
			self.elevator_green = True
		else:
			self.elevator_green = False
		
		#Check to see if Needles should be green.
		# --- Airplane On Ground, Rudder and Aileron Trim set at 0
		if (onground.value) & (abs(self.Aileron.value) < 0.02) & (abs(self.Rudder.value) < 0.02) & (self.elevator_green):
			self.needles_green = True
		else:
			self.needles_green = False
		
class APU_c(object):
	
	def random_EGT_temp(self):
			#From 520 to 580
			self.EGT_temp = int(random.random() * 60 + 520)
		
		
	def __init__(self):
		self.RPM = data_obj(100.0)
		self.EGT = 0
		self.display = False
		self.shutdown_time = 0
		self.random_EGT_temp() # Pick a random EGT temp
		self.count = 0
		
	def calc_EGT(self, delta_t):
		self.count += 1
		if self.count > 2000:
			self.count = 0
			if (random.random() * 5) < 1:
				self.random_EGT_temp()
								
		#Determing Temp
		temp = self.RPM.value * self.EGT_temp / 100.0
		if self.EGT > 520: 
			rate = 0.01
		else:
			rate = 0.06
		self.EGT += (temp-self.EGT) * delta_t * rate
	
	def comp(self, delta_t, curr_time):
		self.calc_EGT(delta_t)
				
		if self.RPM.value > 1: #Running
			self.display = True
			self.shutdown_time = curr_time
		else: #Not Running
			if curr_time - self.shutdown_time > 60: #60 second delay after shutdown guage hidden.
				self.display = False
				
		
	


class Brakes_c(object):
	#The overall brake system.
	#Consists of 4 temperature sensors (one on each main brake)
	#-- Flag if one of the sensors has overheated.
	
	class Temp_Sensor(object):
		#The temperature sensor on each wheel. 
		def __init__(self, pct):
			self.actual_temp = 72  #Units Farhenhight
			self.sensor_temp = 72  #Sensor temp lags actual temp by some time.
			self.disp_number = 1 #
			self.disp_color = green
			self.overtemped = False #Flag to keep indicator at red if brake overheats.
			self.heating_CONST = config.brake_heating_CONST
			self.cooling_CONST = config.brake_cooling_CONST
			self.sensor_CONST = config.brake_sensor_CONST
			self.energy_pct = pct
			
		def heating(self, brake_energy): 
		#Calculates temperature of brake.
			energy = abs(brake_energy * self.energy_pct)
		#Heating of brakes
			self.actual_temp += (energy / self.heating_CONST)
		
		def comp(self, OAT, t):
			#Newton's Cooling Equation T = Tenv + T0 - Tenv * e^-rt
			self.actual_temp = OAT + (self.actual_temp - OAT)*(2.718**(-self.cooling_CONST* t))
			#Sensor temp
			if self.actual_temp < self.sensor_temp: #No delay on cooling of sensor only heating.
				self.sensor_temp = self.actual_temp
			else: #Use conductive heating for sensor_temp
				self.sensor_temp += (self.actual_temp - self.sensor_temp) * self.sensor_CONST * t
			#Display Number Calc
			self.disp_number = int(self.sensor_temp / 95)
			#Limit between 0 and 20. Needed for OAT of less than 0 degrees
			if self.disp_number <0: self.disp_number =0
			elif self.disp_number > 20: self.disp_number = 20
			
			if self.overtemped:
				self.disp_color = red
			elif self.disp_number <= 5:
				self.disp_color = green
			elif self.disp_number <=12:
				self.disp_color = white
			else:
				self.disp_color = red
				self.overtemped = True
				
	
	def get_random_value(self):
		#Used to get a suedo bell curver random number
		#Limit 0.35 to 0.65
		
		min = 0.35
		max = 0.65
		d = max - min
		i = random.random() * d
		i += min
		
		return i
	
	def __init__(self):
		random.seed()
		#Simulator Data Objects
		self.Left_Pedal = data_obj(0)
		self.Right_Pedal = data_obj(0)
		self.Parking_Brake = data_obj(0)
		
		#Get random values for the left and right wheels in each main.
		#This is used to make the brake temp values not equal, some variance.
		LL_pct = self.get_random_value()
		LR_pct = 1 - LL_pct
		RR_pct = self.get_random_value()
		RL_pct = 1 - RR_pct
		
		#print LL_pct, LR_pct, RL_pct, RR_pct
		
		#Brake Temp Sensors
		self.Temp_LL = self.Temp_Sensor(LL_pct) #Temp Left Main Left Main
		self.Temp_LR = self.Temp_Sensor(LR_pct) #Left Main Right Tire
		self.Temp_RL = self.Temp_Sensor(RL_pct) #Right Main Left Tire
		self.Temp_RR = self.Temp_Sensor(RR_pct) #Right Main Right Tire
		
		self.OverTemp = False #Flag if one of sensors has overtemped.
		self.AllNormal = True #Flag is all are sensors are showing green
		#Previous Values for Brake Energy Calculation
		self.prev_time = globaltime.value
		self.prev_v = 0
		
		#Header for Log file
		datafile.activate()
		datafile.write("Actual,Sensor")
	
	def check_flags(self):
		#Check for overtemp
		if (self.Temp_LL.overtemped) | (self.Temp_LR.overtemped) | (self.Temp_RR.overtemped) | (self.Temp_RL.overtemped):
			self.OverTemp = True
		else:
			self.OverTemp = False
		#Check for All Green
		if (self.Temp_LL.disp_color == green) & (self.Temp_LR.disp_color == green) & (self.Temp_RR.disp_color == green) & (self.Temp_RL.disp_color == green):
			self.AllNormal = True
		else:
			self.AllNormal = False
		
	
	def calc_brake_energy(self, aircraft, diff_t):
		#Use Energy equations to determine amount of energy disipated by brakes.
		v = aircraft.airspeed.GS.value * 1.6878 #Convert to ft/sec
		
		thrust = aircraft.Eng_1.Thrust.value + aircraft.Eng_2.Thrust.value
		
		#Thrust Energy E = F x VT
		thrust_energy = thrust * v * diff_t #in lbf*ft
		
		#Airplane Energy due to change in velocity of airplane.
		m = aircraft.total_weight.value * 0.03108 #Convert to mass (slugs)
		airplane_energy = .5*m*(v**2 - self.prev_v**2)
		
		#Drag Energy (no account for pressure / temp changes)
		#E = k * v^3 * t  F= k v^2
		#Correction: After testing looks like its linear according to FSX. ?????
		#-- Linear constant -5120
		drag_energy = -5120 * v * diff_t
		#Overall Energy  thrust + brake = airplane
		brake_energy = airplane_energy - thrust_energy - drag_energy #Units of lbf*ft
		
		#datafile.write("%5.2f,%5.2f,%5.2f,%5.2f,%5.2f" %(brake_energy, airplane_energy, thrust_energy, drag_energy,v))
		
		if abs(brake_energy) > 10000000: #Must be bogus, slewing etc.
			brake_energy = 0
		#Save Previous values
		
		self.prev_v = v
		
		return brake_energy
		
	def comp(self, aircraft):
		#Calculate heating of brakes.
		#Get time differance from last.
		t = aircraft.global_time
		diff_t = t - self.prev_time
		self.prev_time = t
		if diff_t > 3: diff_t = 3
		#if self.Left_Pedal.value < 0:
		#print "LEFT BRAKE",self.Left_Pedal.value
		#For Brakes to Heat up. Must be On Ground, Ias > 0.1, Brake Pedals depressed.
		if ((aircraft.onground.value) & (aircraft.airspeed.IAS.value > 0.1)):
			#Next Check for Brake Pedal depression
			total_pedal = self.Left_Pedal.value + self.Right_Pedal.value
			#print total_pedal
			if (total_pedal) > 0:
				#Calculate percent Force on Left or Right Wheels depending on Brake position.
				Left_Pedal_Pct = self.Left_Pedal.value / total_pedal
				Right_Pedal_Pct = self.Right_Pedal.value / total_pedal
				Brake_Energy = self.calc_brake_energy(aircraft, diff_t)
				left_energy = Brake_Energy * Left_Pedal_Pct
				right_energy = Brake_Energy * Right_Pedal_Pct
				self.Temp_LL.heating(left_energy)
				self.Temp_LR.heating(left_energy)
				self.Temp_RL.heating(right_energy)
				self.Temp_RR.heating(right_energy)
				#print Brake_Energy
			#Cooling of Brakes, sensor delay, and Display Calcs
		OAT_f = aircraft.OAT.value * 1.8 + 32
		self.Temp_LL.comp(OAT_f, diff_t)
		self.Temp_LR.comp(OAT_f, diff_t)
		self.Temp_RL.comp(OAT_f, diff_t)
		self.Temp_RR.comp(OAT_f, diff_t)
		self.check_flags()
		#print self.Temp_LL.actual_temp, self.Temp_LL.sensor_temp, self.AllNormal, self.OverTemp
		datafile.write("%5.2f,%5.2f" %(aircraft.brakes.Temp_LL.actual_temp, aircraft.brakes.Temp_LL.sensor_temp))	
		
		
		
		


class Wheel_c(object):
	def __init__(self, name):
		self.name = name
		self.position = data_obj(0.0) #Range from 0 to 1.0
		
	
class Gear_c(object):
	def __init__(self):
		self.Left = Wheel_c("LEFT")
		self.Right = Wheel_c("RIGHT")
		self.Nose = Wheel_c("NOSE")
		self.handle = data_obj(0)
		self.upandlocked = True
		
	def comp(self):
		if (self.Left.position.value + self.Right.position.value + self.Nose.position.value == 0.0):
			self.upandlocked = True
		else:
			self.upandlocked = False
class flaps_c(object):
	
	def __init__(self):
		#Positions Available
		self.pos_list = []
		#Add positions format, flaps_pos_c(deg, guage_pos, input_value)
		self.pos_list.append(flaps_pos_c(0,0.0,0.0))
		self.pos_list.append(flaps_pos_c(8,0.18,0.18))
		self.pos_list.append(flaps_pos_c(20,0.44,0.44))
		self.pos_list.append(flaps_pos_c(30,0.67,0.67))
		self.pos_list.append(flaps_pos_c(40,1.0,1.0))
		self.num_pos = len(self.pos_list)
		#Create list os flap pos markers, for flap guage
		self.guage_flap_pos = [i.guage_pos for i in self.pos_list]
		#Calculate Slope of pos_list (Used for calculation of guage_pos)
		for i in range(1,self.num_pos):
			run = self.pos_list[i].input_value - self.pos_list[i-1].input_value
			deg_rise = self.pos_list[i].deg - self.pos_list[i-1].deg
			guage_rise = self.pos_list[i].guage_pos - self.pos_list[i-1].guage_pos
			self.pos_list[i].deg_slope = deg_rise / run / 1.0
			self.pos_list[i].guage_slope = guage_rise / run / 1.0
		
		
		
		self.handle = data_obj(2) #Flap Handle Location (UNUSED AS OF NOW)
		self.pos = data_obj(0.44) #Value for FSX
		self.prev_value = 0.0
		self.flap_deg = 0
		self.guage_pos = 0.0
		
	def comp(self):
		#Calculate Guage Postion
		#Assume between 0 and 1, and flap pos_list in ascending order.
		if self.prev_value != self.pos.value:
			flap_value = self.pos.value
			self.prev_value = flap_value
			self.guage_pos = 1.0
			for i in range(1,self.num_pos): #Skip 1st flap pos
				if flap_value <= self.pos_list[i].input_value:
					#Calculate value
					self.flap_deg = round(self.pos_list[i].deg_slope * (flap_value - self.pos_list[i-1].input_value) + self.pos_list[i-1].deg)
					self.guage_pos = round(self.pos_list[i].guage_slope * (flap_value- self.pos_list[i-1].input_value) + self.pos_list[i-1].guage_pos,2)
					break
		
class flaps_pos_c(object):
	def __init__(self, deg, guage_pos, input_value):
		#Data for each position
		#deg = Degree of flap setting
		#guage_pos = 0.0-1.0 where on flap guage location
		#input_value = coresponding input_value from FSX.
		self.deg = deg
		self.guage_pos = guage_pos
		self.input_value = input_value
		self.slope  = 0.0		


class fuel_tank_c(object):
	def __init__(self,value):
		self.gal = data_obj(value)
		self.EICAS_color = green
		if config.use_metric_units:
			self.metric = True
		else:
			self.metric = False
		self.comp()
		
		
	def comp(self):
		if self.metric:
			temp = self.gal.value * 3.04
			self.EICAS_disp = int(round(temp / 5.0) * 5)
		else:
			temp = self.gal.value * 6.7
			self.EICAS_disp = int(round(temp,-1))
		
		#Reset color to green
		if temp >0: self.EICAS_color=green
		else: self.EICAS_color = white
		
class fuel_c(object):
	def __init__(self):
		
		self.left = fuel_tank_c(55.0)
		self.right = fuel_tank_c(86.0)
		self.center = fuel_tank_c(0.0)
		self.total = fuel_tank_c(0.0) #Doesn't retrieve data from FSX, but uses tank class.		
		self.comp()
		
	def wing_color_amber(self):
		
		self.left.EICAS_color = yellow
		self.right.EICAS_color = yellow
	
	def all_color_amber(self):
		self.wing_color_amber()
		self.total.EICAS_color = yellow
		
	def comp(self):
		#LBs/gal 6.7
		self.left.comp()
		self.right.comp()
		self.center.comp()
		self.total.gal.value = self.left.gal.value + self.right.gal.value + self.center.gal.value
		self.total.comp()
		#Calculate EICAS colors
		wing_diff = abs(self.left.EICAS_disp - self.right.EICAS_disp)
		total_qty = self.total.EICAS_disp
		if self.left.metric:
			if wing_diff > 363:
				self.wing_color_amber()
			if total_qty <=405:
				self.all_color_amber()
		else:
			if wing_diff > 800:
				self.wing_color_amber()
			if total_qty <= 900:
				self.all_color_amber()
			
		
class Engine_c(object):
	def __init__(self, number):
		self.number = number
		self.N1 = data_obj(75.0)
		self.N1_text = None
		self.N2 = data_obj(40.0)
		self.Throttle = data_obj(0.0)
		#self.N1_Overspeed = 98.6
		self.ITT = data_obj(700)
		self.Thrust = data_obj(0)
		self.Oil_Pressure = data_obj(123)
		self.Oil_Temp = data_obj(65)
		self.Fuel_Flow = data_obj(2300)
		self.Fuel_Flow_disp = 2300
		self.Fan_Vibration = data_obj(1.2)
		self.lowOil_Pressure = False
		self.running = True
		self.reverser = False
		self.N1_Overspeed_flag = False
		#Constants
		#N1 Overspeed
		self.N1_Overspeed = 98.6
		#N2 Overspeed
		self.N2_Overspeed = 99.3
		#ITT Overtemp
		self.ITT_OverTemp = 900
		#Oil Temp
		self.OilTemp_Red = 163
		self.OilTemp_Amber = 150
		#Oil Pressure
		self.OilPres_Red = 25
		self.OilPres_Amber = 115
		#Fan Vibraton
		self.FANVIB_Yellow = 2.4
		#Used for calculating of Fuel FLow
		self.metric = config.use_metric_units
		
	def decode(self, list):
		self.N1.value = list[0]
		self.N2.value = list[1]
		
	def encode(self):
		return [self.N1.value, self.N2.value]
	def comp(self):
		#Computation
		#  FUEL FLOW Conversion if MEtric units used.
		if self.metric:
			self.Fuel_Flow_disp = int(round(self.Fuel_Flow.value * .4536 /5)*5) #1Kg = .4536 lbs.
		else:
			self.Fuel_Flow_disp = int(round(self.Fuel_Flow.value, -1))
		#Low oilPressure check
		if self.Oil_Pressure.value <= self.OilPres_Red:
			self.lowOil_Pressure = True
		else:
			self.lowOil_Pressure = False
		#Engine running check >55% N2
		if self.N2.value >= 55.0:
			self.running = True
		else:
			self.running = False
		#N1 Overspeed
		if self.N1.value >= self.N1_Overspeed:
			self.N1_Overspeed_flag == True
		else:
			self.N1_Overspeed_flag = False
		#Reverser check
		if self.Throttle.value < 0.0:
			self.reverser = True
			self.N1_text = "REV"
		else:
			self.reverser = False
			self.N1_text = None
			
show_GEARFLAP = show_GEARFLAP_c()

def EICAS_comp(aircraft):
	show_GEARFLAP.comp(aircraft.flaps, aircraft.gear.upandlocked, aircraft.brakes.AllNormal, aircraft.global_time)