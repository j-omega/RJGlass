#!/usr/bin/env python
# ----------------------------------------------------------
# RJGlass Autopilot module
# ----------------------------------------------------------
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


#import aircraft


from guage import globaltime
#class AP_Lmode_c(AP_c):
	#Class of all the Horizontal modes in AP
import config

	
class AP_c(object):
	#The main autopilot class.
	#This is inbetween the PFD FMA and The FSX autopilot, to emulate the RJ AP correctly.
	
	def __init__(self, PFD, attitude, global_time, aircraft):
		self.AP_on = False #Autopilot on or off
		self.Lmode = AP_Lmode_c(PFD.FMA.LNav_act, PFD.FMA.LNav_arm, globaltime.value, aircraft)
		self.Vmode = AP_Vmode_c(PFD.FMA.VNav_act, PFD.FMA.VNav_arm, globaltime.value, aircraft)
		self.FD_on = False
		self.attitude = attitude #attitude guage
		self.aircraft = aircraft
		#self.aileron_pos = 0 #The aileron position sent to FSX -16383 to 16383
		if config.debug_AP:
			self.lnav_debug = open("lnav.txt","w")
			self.lnav_debug.seek(0)
			self.vnav_debug = open("vnav.txt","w")
			self.vnav_debug.seek(0)
	def quit(self):
		if config.debug_AP:
			self.lnav_debug.close()
			self.vnav_debug.close()
			
	def AP_turnon(self):
		self.AP_on = True
		self.FD_turnon()
		
	def AP_turnoff(self):
		self.AP_on = False
		
	def AP_cycle(self):
		if self.AP_on:
			#If AP on then turn off
			self.AP_turnoff()
		else: #If AP off then turn on
			self.AP_turnon()
	
	
	def comp(self, aircraft):
		self.Lmode.control(aircraft)
		self.Vmode.control(aircraft)
		if self.AP_on:
			#Debug
			if config.debug_AP:
				self.lnav_debug.write("%s,%s\n" %(self.Lmode.active.text, self.Lmode.active.debug_text))
				self.vnav_debug.write("%s,%s\n" %(self.Vmode.active.text, self.Vmode.active.debug_text))
			if config.mode != config.TEST:
				aircraft.sevent.eventlist.list[self.aileron_pos.event_id].send()
				aircraft.sevent.eventlist.list[self.elevtrim_pos.event_id].send()
	def FD_turnon(self):
		if self.FD_on == False:
			self.FD_on = True
			self.Lmode.turnon()
			self.Vmode.turnon()
		self.attitude.FD_active.value =-1
		
	def FD_turnoff(self):
		self.FD_on = False
		self.Lmode.turnoff()
		self.Vmode.turnoff()
		self.attitude.FD_active.value =0

		
	def FD_cycle(self):
		if not (self.AP_on): #If APon do nothing
				if self.FD_on: #If FD on then turn off
					self.FD_turnoff()
				else: #If FD off then turn on
					self.FD_turnon() 
			
	def HDG_button(self):
		if self.Lmode.active != self.Lmode.HDG:
			self.Lmode.set_active(self.Lmode.HDG)
			self.FD_turnon() #make sure FD is on
		else:
			self.Lmode.set_active(self.Lmode.ROLL)
			
	def PTCH_inc(self):
		self.PTCH_but(1)
		#self.Vmode.PTCH.desired_pitch += 0.5
		#self.Vmode.set_active(self.Vmode.PTCH)
		#self.FD_turnon()
		
	def PTCH_dec(self):
		self.PTCH_but(-1)
		#self.Vmode.PTCH.desired_pitch -= 0.5
		#self.Vmode.set_active(self.Vmode.PTCH)
		#self.FD_turnon()
		
	def PTCH_but(self, value): #Called if either pitch up or pitch down pressed
		if self.Vmode.active == self.Vmode.VS:
			self.Vmode.VS.VS_ref += (0.1 * value)
			self.Vmode.VS.check_VS_ref() #Make sure between 8 and -8
			self.Vmode.FMA_update(False) #No need to flash mode not changing
		elif self.Vmode.active == self.Vmode.PTCH:
			self.Vmode.PTCH.desired_pitch += (0.5 * value)
		else: #Not in VS or PTCH mode
			self.Vmode.PTCH.desire_pitch = int(self.aircraft.attitude.pitch.value  * 2) / 2.0 #Will round to nearest 0.5
			self.Vmode.set_active(self.Vmode.PTCH)
			self.FD_turnon()
			
	def ALT_button(self):
		pass
	
	def ALT_inc(self):
		self.aircraft.altimeter.bug_inc()
		
	def ALT_dec(self):
		self.aircraft.altimeter.bug_dec()
		
	def VS_button(self):
		if self.Vmode.active != self.Vmode.VS:
			self.Vmode.VS.VS_ref = int(self.aircraft.VSI.value / 100.0)  / 10.0
			self.Vmode.VS.check_VS_ref()
			self.Vmode.set_active(self.Vmode.VS)
			self.FD_turnon() #make sure FD is on
		
		else:
			self.Vmode.set_active(self.Vmode.PTCH)
	
	
		
		
class AP_Vmode_c(AP_c):
	#Class of all the Laternal modes in AP
	def __init__(self, act_disp, arm_disp, global_time, aircraft):
		self.PTCH = Pitch(global_time, aircraft)
		self.ALTS = Alt_Mode(global_time, aircraft)
		self.VS = Vert_Speed(global_time, aircraft)
		self.BLANK = Blank()
		self.on = False
		self.active = self.BLANK
		self.arm = self.BLANK
		self.act_disp = act_disp #FMA disp for active and armed fields
		self.arm_disp = arm_disp
		self.aircraft = aircraft
		
	def control(self, aircraft):
		if self.active == self.PTCH:
			self.PTCH.control(aircraft)
			if self.ALTS.check_capture(aircraft):
				self.set_active(self.ALTS)
		elif self.active == self.VS:
			self.VS.control(aircraft)
			if self.ALTS.check_capture(aircraft):
				self.set_active(self.ALTS)
		#elif self.active == self.HDG:
		#	self.HDG.control(self.ROLL, aircraft)
	def FMA_update(self, flash = True):
		#Update the FMA
		self.act_disp.text = self.active.text
		self.act_disp.end_arrow = self.active.end_arrow
		if flash: self.act_disp.flash()
		self.arm_disp.text = self.arm.text
		self.arm_disp.end_arrow = 0 #Always no arrow on arm
	def set_active(self, mode):
		if self.active != mode:
			self.active = mode
			mode.turnon(True)
			if self.active == self.PTCH:
				self.arm = self.ALTS
			if self.active == self.VS:
				self.arm = self.ALTS
			self.FMA_update()
		else:#mode is already on, so only reset the P, I, and D values so AP doesn't jump.
			mode.turnon(False)
	def turnon(self):
		#This is used to turn on vertical mode when FD or AP is turned on.
		if self.active == self.BLANK:
			self.set_active(self.PTCH)
		#Need to finalize logic diagram.
		self.FMA_update()
		self.on = True
	def turnoff(self):
		self.active = self.BLANK
		self.arm = self.BLANK
		self.FMA_update()
		self.on = False
	
		
class AP_Lmode_c(AP_c):
	#Class of all the Laternal modes in AP
	def __init__(self, act_disp, arm_disp, global_time, aircraft):
		self.ROLL = Roll(global_time, aircraft)
		self.HDG = Heading(global_time, aircraft)
		self.BLANK = Blank()
		self.on = False
		self.active = self.BLANK
		self.arm = self.BLANK
		self.act_disp = act_disp #FMA disp for active and armed fields
		self.arm_disp = arm_disp
		self.aircraft = aircraft
		
	def control(self, aircraft):
		if self.active == self.ROLL:
			self.ROLL.control(aircraft)
		elif self.active == self.HDG:
			self.HDG.control(self.ROLL, aircraft)
	def FMA_update(self, flash=True):
		#Update the FMA
		self.act_disp.text = self.active.text
		self.act_disp.end_arrow = self.active.end_arrow
		if flash: self.act_disp.flash()
		self.arm_disp.text = self.arm.text
		self.arm_disp.end_arrow = 0 #Always no arrow on arm
		
	def set_active(self, mode):
		if self.active != mode:
			self.active = mode
			mode.turnon(True)
			self.FMA_update()
		else: #mode is already on, so reset the P, I, and D values so AP doesn't jump.
			mode.turnon(False)
	def turnon(self):
		if self.active == self.BLANK:
			self.set_active(self.ROLL)
		
		self.FMA_update()
		self.on = True
		
	def turnoff(self):
		self.active = self.BLANK
		self.arm = self.BLANK
		self.FMA_update()
		self.on = False
	
class Alt_Mode(AP_Vmode_c): #ALTS
	def __init__(self, global_time, aircraft):
		self.text = "ALTS"
		self.end_arrow = 0
		self.aircraft = aircraft
		self.debug_text = ""
		#PID Controller here
		#Altitude capture per brother at 3000fpm start capture at 1000 ft out,  500fpm start capture at 50ft
		self.ALT_PID = PID2_c(-1, global_time, None, 0)
		self.ALT_PID.set_gains(0.003, (200000), (0.0000001)) #Set I and P gains to make controller P only
		self.ALT_PID.set_u_limit(8.0) #Limit it to 8000 fpm
		self.ALT_PID.set_I_limit(0.0001)
	def control(self, aircraft):
		#Outputs desired VS to get to capture altitude
		self.ALT_PID.calc(aircraft.altimeter.indicated.value, aircraft.altimeter.bug.value, aircraft.global_time)
		self.debug_text = self.ALT_PID.debug
	def turnon(self, reset):
		pass
	
	def check_capture(self, aircraft): #Used to check if capture is needed
		capture = False
		self.control(aircraft)
		vs = self.ALT_PID.out * 1000
		if vs>=0: #If desired vs + then climb needed to obtain ALT bug.
			if aircraft.VSI.value >= vs: #if aircraft vs > desired vs then
				capture = True	#Initiate ALT capture	
		else: #vs<0  descent needed to obtain ALT bug
			if aircraft.VSI.value <= vs: 
				capture = True
				
		#print vs, aircraft.VSI.value
		return capture
class Vert_Speed(AP_Vmode_c):
	def __init__(self, global_time, aircraft):
		self.text = "ALTS"
		self.text = "VS"
		self.end_arrow = 0
		self.aircraft = aircraft
		#PID Controller here
		self.VS_PID = PID3_c(10000, global_time, aircraft.elev_trim, -16383)
		self.VS_PID.set_gains((0.18* 0.6), (5.5/2), (5.5/8.0))
		self.VS_PID.set_I_limit(0.4)
		self.VS_PID.set_u_limit(0.3)
		#VS reference
		self.VS_ref = 0
		self.debug_text = ""
		
			
	def check_VS_ref(self):
		if self.VS_ref < -8.0: self.VS_ref = -8.0
		if self.VS_ref > 8.0: self.VS_ref = 8.0
		self.determine_text()
		
	def determine_text(self):
		self.text = "VS %2.1f" %abs(self.VS_ref)
		if self.VS_ref >=0.0: 
			self.end_arrow = 1
		else:
			self.end_arrow = -1
	
	def control(self, aircraft):
		self.VS_PID.calc(aircraft.VSI.value/ 1000.0, self.VS_ref, aircraft.global_time)
		aircraft.AP.elevtrim_pos.value = int(self.VS_PID.out)
		#Need to jerry rig FD here
	
	def turnon(self, reset):
		self.VS_PID.turn_on(self.aircraft.attitude.pitch.value)
		
#Each mode has its own class , with common functions to be processed.			
class Pitch(AP_Vmode_c):
	def __init__(self, global_time, aircraft):
		self.text = "PTCH"
		self.end_arrow = 0
		self.aircraft = aircraft
		self.debug_text = ""
		self.pitch_PID = PID2_c(10000, global_time, aircraft.elev_trim, -16383)
		#(0.08), (2 /1.5), (0.4), (1.5/ 8.0), 0.8, -0.8, 1.2, 1.0, 0.1, global_time)
		self.pitch_PID.set_gains((0.08), (2/1.5), (1.5/8))
		self.pitch_PID.set_I_limit(0.4)
		self.pitch_PID.set_u_limit(0.8)
		self.pitch_PID.set_Roc_curve(1.2, 1.0, 0.1)
		self.desired_pitch = 0.0 #This is what pitch PTCH mode will hold
	def control(self, aircraft):
		self.pitch_PID.calc(aircraft.attitude.pitch.value, self.desired_pitch, aircraft.global_time)
		self.debug_text = self.pitch_PID.debug
		#print self.bank_PID.Kp, self.bank_PID.P, self.bank_PID.I, self.bank_PID.D, globaltime.value
		aircraft.AP.elevtrim_pos.value = int(self.pitch_PID.out)
		aircraft.attitude.FD_pitch.value = self.desired_pitch
		
	def turnon(self, reset):
		
		if reset: self.reset_desired_pitch()
		self.pitch_PID.turn_on(self.desired_pitch)
		#self.pitch_PID.turn_on(self.aircraft.attitude.pitch.value)
	def reset_desired_pitch(self):
		#If pitch mode active will hold current pitch
		self.desired_pitch = self.aircraft.attitude.pitch.value
		
	

class Roll(AP_Lmode_c):
	#The Roll mode. If at time of activation if under 5 degrees of bank, then AP hold 0 bank, if >5degree holds that degree.
	def __init__(self, global_time, aircraft):
		self.text = "ROLL"
		self.end_arrow = 0
		self.aircraft = aircraft
		self.debug_text = ""
		#self.PID = PID_c(0.5, 0.1, 0.2, 0.0, 0.01, 0.000001, 1.0, -1.0, global_time)
		self.bank_PID = PID2_c(-16383, global_time, aircraft.aileron_pos, -16383)
		self.bank_PID.set_gains((0.35* 0.5), (2/1.5), (1.5 /8))
		#self.bank_PID.set_gains((0.25* 0.5), (2/1.5), (1.5 /8))
		self.bank_PID.set_I_limit(0.4)
		self.bank_PID.set_u_limit(0.6)
		self.bank_PID.set_Roc_curve(66.0, 0.2, 10000.3)
		self.desired_bank = 0.0 #This is what bank ROLL mode will hold
	def control(self, aircraft):
		self.bank_PID.calc(aircraft.attitude.bank.value, self.desired_bank, aircraft.global_time)
		self.debug_text = self.bank_PID.debug
		#print self.bank_PID.Kp, self.bank_PID.P, self.bank_PID.I, self.bank_PID.D, globaltime.value
		aircraft.AP.aileron_pos.value = int(self.bank_PID.out)
		aircraft.attitude.FD_bank.value = self.desired_bank
		
	def turnon(self, reset= False):
		self.bank_PID.turn_on(self.aircraft.attitude.bank.value)
		if reset: self.reset_desired_bank()
		
	def reset_desired_bank(self):
		#If current aircraft bank is less than 5deg, then 0 otherwise hold current bank.
		temp = self.aircraft.attitude.bank.value
		
		if (-5.0 < temp < 5.0):
			self.desired_bank = 0.0
		else:
			self.desired_bank = temp
			
		
	
class Blank(object):
	#This is for a blank display, if AP is off, or no armed mode.
	def __init__(self):
		self.text = ""
		self.end_arrow = 0
		self.debug_text = ""
	def control(self, aircraft):
		#DO NOTHING
		pass
	
	def turnon(self, reset = False):
		pass
	
class Heading(AP_Lmode_c):
	def __init__(self, global_time, aircraft):
		self.text = "HDG"
		self.end_arrow = 0
		self.aircraft = aircraft
		self.heading_PID = PID2_c(-30.0, global_time, aircraft.attitude.bank, -30.0)
		self.heading_PID.set_gains((0.08), (5), (0.00001))
		self.heading_PID.set_I_limit(0.05)
		self.heading_PID.set_u_limit(1.0)
		#self.heading_PID.out = 0.0
		self.debug_text = ""
		
	def control(self, ROLL, aircraft):
		self.heading_PID.calc(aircraft.HSI.Mag_Heading.value,  aircraft.HSI.Heading_Bug.value, aircraft.global_time, True)
		self.debug_text = self.heading_PID.debug
		ROLL.desired_bank = -self.heading_PID.out
		ROLL.control(aircraft)
		
	def turnon(self, reset=False):
		pass

class PID_c(AP_c):
	
	def __init__(self, Kp, alpha, beta, gamma, Ti, Td, u_max, u_min, global_time):
		self.Kp = Kp #0.5
		self.beta = beta #0.2
		self.alpha = alpha #0.1
		self.gamma = gamma #0.0
		self.Ti = Ti #0.01
		self.Td = Td #0.000001
		self.u_min =  u_min #-1.0
		self.u_max = u_max #1.0
		self.u = 0.0
		self.eDf_prev = 0.0
		self.eDf_prevprev = 0.0
		self.eP_prev = 0.0
		self.last_time = global_time
		
	
	def calc(self,measured, reference, time):
		
		#Just calculate it
		Ts = time- self.last_time
		self.last_time = time
		if Ts <= 0.0: Ts = 0.0001
		error = measured - reference
		eP = self.beta * error
		eD = self.gamma * error
		#Deriviative Part
		TsoverTf = Ts / (self.alpha * self.Td)
		eDf = self.eDf_prev / (TsoverTf +1) + eD *TsoverTf / (TsoverTf +1)
		D = self.Td / Ts * (eDf - 2 *self.eDf_prev + self.eDf_prevprev)
		#Integral Part
		I  = Ts / self.Ti * error
		#Proportianal Part
		P = eP - self.eP_prev
		self.u += self.Kp * (P+I+D)
		#Check for max deflection
		if self.u > self.u_max:
			self.u = self.u_max
		elif self.u < self.u_min:
			self.u = self.u_min
		#Calculate previous
		self.eP_prev = eP
		self.eDf_prevprev = self.eDf_prev
		self.eDf_prev = eDf
		
class PID2_c(AP_c):
	
	def __init__(self, multiplier, global_time, output_ref, output_ref_factor = 1.0):
		#The overall multipler for the output, and a output refernce, so I of PID controller can be preloaded correctly.
		#to eliminate ump of output.
		self.multiplier = multiplier
		self.output_ref = output_ref #only used during turn_on method so control surfaces don't jump. (Preloads I)
		self.output_ref_factor = output_ref_factor #used in case output_ref need to by multipled by a factor
		self.Kp = 1.0 #0.5
		self.Ti = 1.0
		self.Td = 1.0
		self.u_min =  -1.0
		self.u_max = 1.0
		self.u = 0.0
		self.last_time = global_time
		self.prev_error = 0.0
		self.I = 0.0
		self.P = 0.0
		self.D = 0.0
		self.I_limit = 1.0 / self.Kp
		self.max_Roc = 100000.0
		self.min_Roc = 10000.0
		self.Ref = 0.0
		self.curve_slope = 10000.0
		self.max_Roc_limit = 0.0
		self.out = 0.0
		self.debug = "" #Debug text
	def set_gains(self, Kp, Ti, Td):
		self.Kp = Kp
		self.Ti = Ti
		self.Td = Td
	
	def set_u_limit(self, umax, umin = None):
		#if u min not given, then make it -1 * umax
		if umin == None:
			umin = umax * -1.0
		self.u_min = umin
		self.u_max = umax
		
	def set_I_limit(self, I_limit):
		self.I_limit = I_limit / self.Kp
	
	def set_Roc_curve(self, max, min, slope):
		self.max_Roc = max
		self.min_Roc = min
		self.curve_slope = slope
		
	def turn_on(self, current_reference):
		#This is used to set the u and prev_error correctly, so when AP turn on, control wont jump.
		self.I = (self.output_ref.value * self.output_ref_factor / self.multiplier) / self.Kp
		self.Ref = current_reference
		self.prev_error = 0.0
	
	def calc(self,measured, reference, time, check180 = False):
		#check180 will make sure error is within +/- 180 used for heading hold.
		#Just calculate it
		dt = time - self.last_time
		#Main part of PID controller
		if dt <= 0.0: dt = 0.001 #prevent divide by 0
		
		self.last_time = time
		
		#Slow down change of reference with curve
		#self.max_Roc_limit += self.curve_slope # * dt * 3
		self.max_Roc_limit = self.max_Roc
		if self.max_Roc_limit > self.max_Roc:
			self.max_Roc_limit = self.max_Roc
		max = dt * self.max_Roc_limit
		min = dt * self.min_Roc 
		curve = (reference - self.Ref) * self.curve_slope * dt
		
		#if curve >0:
	#		sign = 1
		#else: sign = -1
		a_curve = abs(curve)
		if a_curve > max:
			a_curve = max
		else:
			#Curve is limiting max therefore make roc limit equal to curve
			self.max_Roc_limit = a_curve / dt
			if a_curve < min:
				a_curve = min
		
		if reference > self.Ref:
			#if a_curve == max:
			#	self.Ref = measured + a_curve
			#else:
			self.Ref += a_curve
			if self.Ref > reference:
				self.Ref = reference
		else: #reference < self.Ref
			#if a_curve == max:
			#	self.Ref = measured - a_curve
			#else:
			self.Ref -= a_curve
			if self.Ref < reference:
				self.Ref = reference
				
		
		#Find overall error
		error = measured - self.Ref
		#This makes sure error is within +/-180 only used for heading hold.
		if check180:
			if error<-180.0: error+=360.0
			elif error>180.0: error-=360.0
			
		#Deriviative Part
		self.D = self.Td * (error - self.prev_error) / dt
		#Integral Part
		self.I  = self.I + (1/ self.Ti) * error * dt
		
		#Limit I if over I_limit
		if self.I > self.I_limit:
			self.I = self.I_limit
		elif self.I < -self.I_limit:
			self.I = -self.I_limit
		
			
		#Proportianal Part
		self.P = error
		
		self.u = self.Kp * (self.P+self.I+self.D)
		#Check for max deflection Limit u
		if self.u > self.u_max:
			self.u = self.u_max
		elif self.u < self.u_min:
			self.u = self.u_min
		#Calculate previous
		self.prev_error = error
		#Multiply by overall multplier converts it to FSX value
		self.out = self.u * self.multiplier
		
		self.debug =  self.outdata(measured, reference, time)
		
	
	
	def outdata(self, measured,reference, time):
		#Just output the data of the important variables in the PID controller for debugging.
		#Measured, reference, output
		s = "%7.3f,%f,%f,%f,%f,%f,%f,%f,%f" %(time,measured, reference, self.Ref,self.out, self.u, self.P, self.I, self.D)
		return s

class PID3_c(AP_c):
	
	def __init__(self, multiplier, global_time, output_ref, output_ref_factor = 1.0):
		#The overall multipler for the output, and a output refernce, so I of PID controller can be preloaded correctly.
		#to eliminate ump of output.
		self.multiplier = multiplier
		self.output_ref = output_ref #only used during turn_on method so control surfaces don't jump. (Preloads I)
		self.output_ref_factor = output_ref_factor #used in case output_ref need to by multipled by a factor
		self.Kp = 1.0 #0.5
		self.Ti = 1.0
		self.out = 0.0
		self.Td = 1.0
		self.u_min =  -1.0
		self.u_max = 1.0
		self.u = 0.0
		self.last_time = global_time
		self.prev_a_error = 0.0
		self.prev_d_error = 0.0
		self.prev_error = 0.0
		self.I = 0.0
		self.P = 0.0
		self.D = 0.0
		self.I_limit = 1.0 / self.Kp
		self.max_Roc = 100000.0
		self.min_Roc = 10000.0
		self.Ref = 0.0
		self.curve_slope = 10000.0
		self.max_Roc_limit = 0.0
		self.a_list=[]
		self.a_limit = 0.1
	def set_gains(self, Kp, Ti, Td):
		self.Kp = Kp
		self.Ti = Ti
		self.Td = Td
	
	def set_u_limit(self, umax, umin = None):
		#if u min not given, then make it -1 * umax
		if umin == None:
			umin = umax * -1.0
		self.u_min = umin
		self.u_max = umax
		
	def set_I_limit(self, I_limit):
		self.I_limit = I_limit / self.Kp
	
	def set_Roc_curve(self, max, min, slope):
		self.max_Roc = max
		self.min_Roc = min
		self.curve_slope = slope
		
	def turn_on(self, current_reference):
		#This is used to set the u and prev_error correctly, so when AP turn on, control wont jump.
		self.I = (self.output_ref.value * self.output_ref_factor / self.multiplier) / self.Kp
		self.Ref = current_reference
		self.prev_error = 0.0
	
	def calc(self,measured, reference, time, check180 = False):
		#check180 will make sure error is within +/- 180 used for heading hold.
		#Just calculate it
		dt = time - self.last_time
		self.last_time = time
		
		
		
				
		#Main part of PID controller
		if dt <= 0.0: dt = 0.000001 #prevent divide by 0
		#Find overall error
		error = measured - reference
		
		#This makes sure error is within +/-180 only used for heading hold.
		if check180:
			if error<-180.0: error+=360.0
			elif error>180.0: error-=360.0
		
		#Use linear relationship to determine change in value desired
		a_reference = error * 0.15 #Desired acceleration toward capture value
		if a_reference > self.a_limit:
			a_reference = self.a_limit
		elif a_reference < -self.a_limit:
			a_reference = -self.a_limit
		self.a_list.append(self.prev_error - error)
		if len(self.a_list) >10:
			self.a_list.pop(0)
		avg = sum(self.a_list)/ len(self.a_list)
		
				#This is the change in error per second
		#accel = (self.prev_error - error) / dt
		accel = (avg) / dt
		self.Ref = accel
		a_error = accel - a_reference #error in change of error (acceleration of error)
		#Deriviative Part
		self.D = self.Td * (a_error - self.prev_a_error) / dt
		#Integral Part
		self.I  = self.I + (1/ self.Ti) * a_error * dt
		
		#Limit I if over I_limit
		if self.I > self.I_limit:
			self.I = self.I_limit
		elif self.I < -self.I_limit:
			self.I = -self.I_limit
		
			
		#Proportianal Part
		self.P = a_error
		
		self.u = self.Kp * (self.P+self.I+self.D)
		#Check for max deflection Limit u
		if self.u > self.u_max:
			self.u = self.u_max
		elif self.u < self.u_min:
			self.u = self.u_min
		#Calculate previous
		self.prev_a_error = a_error
		#self.prev_d_error = d_error
		self.prev_error = error
		#Multiply by overall multplier converts it to FSX value
		self.out = self.u * self.multiplier
		
class CAPTURE_EQU_c(AP_c):
	#This is used for a capature equation for altitude, and possibly speed hold.
	def __init__(self, multiplier):
		#The overall multipler for the output, and a output refernce, so I of PID controller can be preloaded correctly.
		#to eliminate ump of output.
		self.multiplier = multiplier
		self.u_min =  -1.0
		self.u_max = 1.0
		self.u = 0.0
		self.P = 0.0
		
	def set_u_limit(self, umax, umin = None):
		#if u min not given, then make it -1 * umax
		if umin == None:
			umin = umax * -1.0
		self.u_min = umin
		self.u_max = umax
	def set_Kp_limit(self, Kp):
		self.Kp = Kp
	
	
	def calc(self,measured, reference):
		#Just calculate it
		
		#Find overall error
		error = measured - reference 
		self.P = error			
		#Proportianal Part
		self.u = self.Kp * (self.P)
		#Check for max deflection Limit u
		if self.u > self.u_max:
			self.u = self.u_max
		elif self.u < self.u_min:
			self.u = self.u_min
		#Calculate previous
		#Multiply by overall multplier converts it to FSX value
		self.out = self.u * self.multiplier
		
class PID4_c(AP_c):
	
	def __init__(self, multiplier, global_time, output_ref, output_ref_factor = 1.0):
		#The overall multipler for the output, and a output refernce, so I of PID controller can be preloaded correctly.
		#to eliminate ump of output.
		self.multiplier = multiplier
		self.output_ref = output_ref #only used during turn_on method so control surfaces don't jump. (Preloads I)
		self.output_ref_factor = output_ref_factor #used in case output_ref need to by multipled by a factor
		self.Kp = 1.0 #0.5
		self.Ti = 1.0
		self.Td = 1.0
		self.u_min =  -1.0
		self.u_max = 1.0
		self.u = 0.0
		self.last_time = global_time
		self.prev_error = 0.0
		self.I = 0.0
		self.P = 0.0
		self.D = 0.0
		self.I_limit = 1.0 / self.Kp
		self.max_Roc = 100000.0
		self.min_Roc = 10000.0
		self.Ref = 0.0
		self.curve_slope = 10000.0
		self.max_Roc_limit = 0.0
		
	def set_gains(self, Kp, Ti, Td):
		self.Kp = Kp
		self.Ti = Ti
		self.Td = Td
	
	def set_u_limit(self, umax, umin = None):
		#if u min not given, then make it -1 * umax
		if umin == None:
			umin = umax * -1.0
		self.u_min = umin
		self.u_max = umax
		
	def set_I_limit(self, I_limit):
		self.I_limit = I_limit / self.Kp
	
	def set_Roc_curve(self, max, min, slope):
		self.max_Roc = max
		self.min_Roc = min
		self.curve_slope = slope
		
	def turn_on(self, current_reference):
		#This is used to set the u and prev_error correctly, so when AP turn on, control wont jump.
		self.I = (self.output_ref.value * self.output_ref_factor / self.multiplier) / self.Kp
		self.Ref = current_reference
		self.prev_error = 0.0
	
	def calc(self,measured, reference, time, check180 = False):
		#check180 will make sure error is within +/- 180 used for heading hold.
		#Just calculate it
		dt = time - self.last_time
		self.last_time = time
		
		#Slow down change of reference with curve
		self.max_Roc_limit += self.curve_slope # * dt * 3
		if self.max_Roc_limit > self.max_Roc:
			self.max_Roc_limit = self.max_Roc
		max = dt * self.max_Roc_limit
		min = dt * self.min_Roc 
		curve = (reference - self.Ref) * self.curve_slope * dt
		
		#if curve >0:
	#		sign = 1
		#else: sign = -1
		a_curve = abs(curve)
		if a_curve > max:
			a_curve = max
		else:
			#Curve is limiting max therefore make roc limit equal to curve
			self.max_Roc_limit = a_curve / dt
			if a_curve < min:
				a_curve = min
		
		if reference > self.Ref:
			self.Ref += a_curve
			if self.Ref > reference:
				self.Ref = reference
		else: #reference < self.Ref
			self.Ref -= a_curve
			if self.Ref < reference:
				self.Ref = reference
				
		#Main part of PID controller
		if dt <= 0.0: dt = 0.000001 #prevent divide by 0
		#Find overall error
		error = measured - self.Ref
		#This makes sure error is within +/-180 only used for heading hold.
		if check180:
			if error<-180.0: error+=360.0
			elif error>180.0: error-=360.0
			
		#Deriviative Part
		self.D = self.Td * (error - self.prev_error) / dt
		#Integral Part
		self.I  = self.I + (1/ self.Ti) * error * dt
		
		#Limit I if over I_limit
		if self.I > self.I_limit:
			self.I = self.I_limit
		elif self.I < -self.I_limit:
			self.I = -self.I_limit
		
			
		#Proportianal Part
		self.P = error
		
		self.u = self.Kp * (self.P+self.I+self.D)
		#Check for max deflection Limit u
		if self.u > self.u_max:
			self.u = self.u_max
		elif self.u < self.u_min:
			self.u = self.u_min
		#Calculate previous
		self.prev_error = error
		#Multiply by overall multplier converts it to FSX value
		self.out = self.u * self.multiplier
