#!/usr/bin/env python
# ----------------------------------------------------------
# EICAS2_mod MODULE for GlassCockpit procject RJGlass (Main Right EICAS screen)
# ----------------------------------------------------------
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

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import EICAS_data
import time
import sys, os
import math, pickle
import config
#from EICAS1_mod import Dial_Guage
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

from guage import * #All add on guage functions colors etc.
from EICAS_guage import *
#class scissor(

class arcs_c(object):
		def __init__(self, color, start_angle=0, stop_angle=0 , list= []):
			self.color = color
			self.list = list
			self.start_angle = start_angle
			self.stop_angle = stop_angle
			if len(list) == 0:
				self.active = False
			else:
				self.active = True
			
		def within(self, angle):
			if (self.start_angle <= angle <= self.stop_angle):
				return True
			else:
				return False
		def draw(self):
			glColor(self.color)
			glBegin(GL_LINE_STRIP)
			Draw_List(self.list)
			glEnd()
			

def calc_arc(radius, start, stop, steps):
			#Creates draw list for the arcs on each side of aileron trim.
			step = (stop - start) / steps
			angle= start
			l = []
			for i in range(steps):
				l+= List_Circle(radius, 5, angle, angle + step, True, True, radius-5)
			#def List_Circle(radius, segments, start_angle = 0, stop_angle = 360, start_tick = False, stop_tick = False, tick_radius = 0):
				angle+= step
			return l


class EICAS2_guage(object):
	
	
	class Trim_c(object):
		#Trim display, elevator, airleron and rudder
		
		class Aileron_Trim(object):
			#Ailerton trim
			
			def __init__(self, x,y, radius):
				self.x = x
				self.y = y
				self.left_arc = calc_arc(radius, -30, -150, 4)
				self.right_arc = calc_arc(radius,30, 150, 4)
				self.max_angle = 60
				self.line_radius = radius - 12
				self.lwd_label = Guage_Label(-52, -73, 'LWD')
				self.rwd_label = Guage_Label(20, -73, 'RWD')
				self.ail_label = Guage_Label(-17, 77, 'AIL')
			def draw(self, value, needles_green):
				angle = value * self.max_angle
				glPushMatrix()
				glTranslatef(self.x, self.y, 0)
				#Draw right arc
				glBegin(GL_LINE_STRIP)
				Draw_List(self.right_arc)
				glEnd()
				#Draw left arc
				glBegin(GL_LINE_STRIP)
				Draw_List(self.left_arc)
				glEnd()
				#Draw Trim line
				if needles_green:
					glColor(green)
				glPushMatrix()
				glRotate(-angle,0,0,1)
				glBegin(GL_LINES)
				glVertex2f(-self.line_radius,0)
				glVertex2f(self.line_radius,0)
				#Draw two small lines to make dot in center
				glVertex2f(-2,1)
				glVertex2f(2,1)
				glVertex2f(-2,-1)
				glVertex2f(2,-1)
				glEnd()
				glPopMatrix() #Draw Trim Line
				#Draw Labels
				self.lwd_label.draw()
				self.rwd_label.draw()
				self.ail_label.draw()
				glPopMatrix()
		class Rudder_Trim(object):
			#Rudder trim
				
			def __init__(self, x,y):
				self.x = x
				self.y = y
				radius = 58
				self.arc = calc_arc(radius, 120,240, 4)
				self.max_angle = 60
				self.line_radius = radius -14
				self.nl_label = Guage_Label(-65, 2, 'NL')
				self.nr_label = Guage_Label(43, 2, 'NR')
				self.rudder_label = Guage_Label(-35, 22, 'RUDDER')
			def draw(self, value, needles_green):
				angle = value * self.max_angle
				glPushMatrix()
				glTranslatef(self.x, self.y, 0)
				#Draw arc
				glBegin(GL_LINE_STRIP)
				Draw_List(self.arc)
				glEnd()
				if needles_green:
					glColor(green)
				#Draw Trim line
				glPushMatrix()
				glRotate(angle,0,0,1)
				glBegin(GL_LINES)
				glVertex2f(0,0)
				glVertex2f(0,-self.line_radius)
				#Draw two small lines to make dot in center
				glVertex2f(-2,1)
				glVertex2f(2,1)
				glVertex2f(-2,-1)
				glVertex2f(2,-1)
				glEnd()
				glPopMatrix() #Draw Trim Line
				#Draw Labels
				self.nl_label.draw()
				self.nr_label.draw()
				self.rudder_label.draw()
				glPopMatrix()	
				
		class Elevator_Trim(object):
			#Elevator trim
				
			def __init__(self, x,y):
				self.x = x
				self.y = y
				self.height = 95
				self.step = self.height / 15.0
				#Load up in memory y locations for vertical line
				self.y_3 = 3 * self.step
				self.y_9 = 9 * self.step
				self.y_5 = 5 * self.step
				self.y_10 = 10 * self.step
				self.y_15 = 15 * self.step
							
				#Labels			
				self.nu_label = Guage_Label(-22, 105, 'NU')
				self.nd_label = Guage_Label(-22, -25, 'ND')
				self.stab_label = Guage_Label(9, 125, 'STAB')
			
			def draw_box(self, value):
				#Draw box with 0.0-15.0 value inside of it.
				glPushMatrix()
				#Move to Correct location
				glTranslatef(0,value * self.step,0)
				#Draw box
				#Demensions
				x1 = 12
				x2 = 16
				x3 = 70
				h = 13
				glBegin(GL_LINE_STRIP)
				glVertex2f(0,0)
				glVertex2f(x1,0)
				glVertex2f(x2,h)
				glVertex2f(x3,h)
				glVertex2f(x3,-h)
				glVertex2f(x2,-h)
				glVertex2f(x1,0)
				glEnd()
				#Text
				glTranslatef(15,-9,0)
				scale = 0.18
				glScalef(scale,scale,1.0)
				s = "%4.1f" %(value)
				glText(s)		
				
				glPopMatrix()
				
			
			def draw(self, value, elev_green):
				glPushMatrix()
				glTranslatef(self.x, self.y, 0)
				#Draw vertical line
				glColor(white)
				glBegin(GL_LINE_STRIP)
				glVertex2f(0, 0)
				glVertex2f(0, self.y_3)
				glEnd()
				glColor(green)
				glBegin(GL_LINE_STRIP)
				glVertex2f(0, self.y_3)
				glVertex2f(0, self.y_9)
				glEnd()
				glColor(white)
				glBegin(GL_LINE_STRIP)
				glVertex2f(0, self.y_9)			
				glVertex2f(0, self.y_15)
				glEnd()
				#Draw Tick marks
				x = 10
				end_y = 0
				# --- White Ticks
				glBegin(GL_LINES)
				glVertex2f(0, 0)
				glVertex2f(x, -end_y)
				glVertex2f(0, self.y_5)
				glVertex2f(x, self.y_5)
				glVertex2f(0, self.y_10)
				glVertex2f(x, self.y_10)
				glVertex2f(0, self.y_15)
				glVertex2f(x, self.y_15 +end_y)
				
				
				glEnd()
				#Draw Box
				#Round to 0.2 divisions per Jeff
				text_value = round(value *5) / 5
				#glTranslatef(0,globaltest.one,0)
				if elev_green:
					glColor(green)
				self.draw_box(text_value)
				
				#Draw Labels
				self.stab_label.draw()
				self.nu_label.draw()
				self.nd_label.draw()
				
				glPopMatrix()	
				
				
		def __init__(self,x,y):
			self.x = x
			self.y = y
			
			self.trim_label=Guage_Label(0,0,'-TRIM-')
			self.aileron = self.Aileron_Trim(-29, -83, 60)
			self.rudder = self.Rudder_Trim(26, -220)
			self.elevator = self.Elevator_Trim(75, -131)
			
		def draw(self, trim):
			glPushMatrix()
			glTranslatef(self.x, self.y, 0)
			self.trim_label.draw()
			self.aileron.draw(trim.Aileron.value, trim.needles_green)
			self.elevator.draw(trim.Elevator.value, trim.elevator_green)
			self.rudder.draw(trim.Rudder.value, trim.needles_green)
			
			glPopMatrix()
	
	class APU_Guages(object):
		#RPM and EGT APU Guages
		def __init__(self,x,y):
			self.x = x
			self.y = y
			
			self.APU_label = Guage_Label(0,0,"APU")
			
			#RPM Guage
			self.RPM = Dial_Guage(-48, -68, 55, 90, 330, 0, 107.0, 0, 107.0, "%3d", True)
			self.RPM.green_arc = self.RPM.arc(green, 25, 0, 100.0, True, False)
			self.RPM.amber_arc = self.RPM.arc(yellow,5, 100.1, 106.0, False, False)
			self.RPM.red_arc = self.RPM.arc(red,5, 106.0, 107.0, False, True)
			self.RPM.text_x = -15 #Text offset 
			self.RPM.text_y = 14 
			self.RPM_label = Guage_Label(-68,-144,"RPM")
				
			#EGT Guage
			self.EGT = Dial_Guage(82,-68,55,90,250, 0, 744, 0, 744, "%3d", True)
			self.EGT.green_arc = self.EGT.arc(green, 25, 0, 710.0, True, False)
			self.EGT.amber_arc = self.EGT.arc(yellow,5, 710.1, 743, False, False)
			self.EGT.red_arc = self.EGT.arc(red,5, 743.1, 744, False, True)
			self.EGT.text_x = 1 #Text offset 
			self.EGT.text_y = 14 
			self.EGT_label = Guage_Label(66,-144,"EGT")
			
			#Door Label
			self.Door_label = Guage_Label(-92,-181, "DOOR OPEN", size=0.15)
			
		def draw(self, APU):
			glPushMatrix()
			glTranslatef(self.x,self.y,0)
			if APU.display == False: 
				glPushMatrix()
				glTranslatef(-89,-157,0) #APU label is in different spot
				self.APU_label.draw()
				glPopMatrix()
			else: #APU Running show guages.
				self.APU_label.draw()
				self.RPM.draw(round(APU.RPM.value,0))
				self.EGT.draw(round(APU.EGT,0))
				self.RPM_label.draw()
				self.EGT_label.draw()
			#Door Check
			if APU.RPM.value > 5:
				self.Door_label.text = "DOOR OPEN"
			else:
				self.Door_label.text = "DOOR CLSD"
			self.Door_label.draw()
			glPopMatrix()
			
	class Brake_Temp_Guages(object):
		#Brake temperatuer guages bottom right of screen.
		
		class Brake_Temp_Indicator(object):
			#4 Indicators of brake temp.
			def __init__(self, x,y):
				self.x = x
				self.y = y
				
			def draw(self, temp_sensor):
				glPushMatrix()
				glTranslatef(self.x,self.y,0)
				
				glColor(temp_sensor.disp_color)
				
				#Draw Outside box
				w = 24
				h = 16
				glBegin(GL_LINE_LOOP)
				glVertex2f(w,h)
				glVertex2f(-w,h)
				glVertex2f(-w,-h)
				glVertex2f(w,-h)
				glEnd()
				#Draw Text Value
				glTranslatef(-14,-9,0)
				glScale(0.18,0.18,1.0)
				glText("%02d" %temp_sensor.disp_number)
				glPopMatrix()
				
		def __init__(self,x,y):
			self.x = x
			self.y = y
			#Brakes appear, when Gear or Flap is down
			self.show = EICAS_data.show_GEARFLAP
			#Brake Temp Label
			self.Brake_Temp_label = Guage_Label(-54,23,"BRAKE TEMP")
			#Brake Indicators
			x1 = 87
			x2 = 29
			y = 0
			self.Brake_LL = self.Brake_Temp_Indicator(-x1,y)
			self.Brake_LR = self.Brake_Temp_Indicator(-x2,y)
			self.Brake_RL = self.Brake_Temp_Indicator(x2,y)
			self.Brake_RR = self.Brake_Temp_Indicator(x1,y)
			
			
		def draw(self, brakes_data):
			if self.show.show:
				glPushMatrix()
				glTranslatef(self.x,self.y,0)
				#Draw Label
				self.Brake_Temp_label.draw()
				#Draw Boxes
				self.Brake_LL.draw(brakes_data.Temp_LL)
				self.Brake_LR.draw(brakes_data.Temp_LR)
				self.Brake_RL.draw(brakes_data.Temp_RL)
				self.Brake_RR.draw(brakes_data.Temp_RR)
				glPopMatrix()
			
	class Cabin_Pressure_Guages(object):
		#RPM and EGT APU Guages
		
		
		class Delta_P_label_c(Guage_Label):
			#
			def draw_delta(self):
				#Draw the Delta Symbol
				w = 5
				h = -13
				
				glPushMatrix()
				glTranslatef(-28,-95,0)
				glBegin(GL_LINE_LOOP)
				glVertex2f(0,0)
				glVertex2f(-w,h)
				glVertex2f(w,h)
				glEnd()
				glPopMatrix()
				
		class CTEMP_label_c(Guage_Label):
			
			def draw_deg_C(self):
				#Draw Circle
				glPushMatrix()
				glTranslatef(93,-14,0)
				glColor(white)
				glCircle(3,6)
				#Draw Small C
				glTranslatef(4,-12,0)
				glScalef(0.12,0.12,1.0)
				glText("C")
				glPopMatrix()
				
				
		
		def label_pos_calc(self, line,text):
			spacing = -27
			#Used to return the Guage_Label.
			y = spacing * line
			x = int(-0.12* 95 * len(text))
			return x,y
					
		def label_create(self, line, text):
			
			x,y= self.label_pos_calc(line,text)
			return Guage_Label(x,y,text)
		
		def value_create(self, line, text, color):
			
			x,y = self.label_pos_calc(line,text)
			#Ignore X since its left justified.
			x = 37
			return Guage_Label(x,y-2,text, 0.18, color)
		
		def __init__(self,x,y):
			self.x = x
			self.y = y
						
			#Left collum labels
			self.OXY_label = self.label_create(0,"OXY")
			self.OXY_value = self.value_create(0,"1420",green)
			self.CTEMP_label = self.label_create(1,"C TEMP")
			c_x,c_y = self.label_pos_calc(1,"C")
			self.CTEMP_value = self.CTEMP_label_c(37, c_y-2, " 25", 0.18)
			self.CALT_label = self.label_create(2,"C ALT")
			self.CALT_value = self.value_create(2,"300",green)
			self.RATE_label = self.label_create(3,"RATE")
			self.RATE_value = self.value_create(3,"4",green)
			p_x,p_y = self.label_pos_calc(4,"P")
			self.DELTAP_label = self.Delta_P_label_c(p_x,p_y,"P")
			self.DELTAP_value = self.value_create(4,"0.0",green)
			self.LDGELEV_label = self.label_create(5,"LDG ELEV")
			self.LDGELEV_value = self.value_create(5,"320",cyan)
		
		def draw(self):
			glPushMatrix()
			glTranslatef(self.x, self.y,0)
			self.OXY_label.draw()
			self.OXY_value.draw("1900")
			self.CTEMP_label.draw()
			self.CTEMP_value.draw()
			self.CTEMP_value.draw_deg_C()
			self.CALT_label.draw()
			self.CALT_value.draw()
			self.RATE_label.draw()
			self.RATE_value.draw()
			self.DELTAP_label.draw()
			self.DELTAP_label.draw_delta()
			self.DELTAP_value.draw()
			self.LDGELEV_label.draw()
			self.LDGELEV_value.draw()
			glPopMatrix()
			
	def load_texture(self):
			self.bg_image = texture_image('images/EICAS_R.png')	
	
	def __init__(self):
		
		self.trim=self.Trim_c(100,592)
		self.APU = self.APU_Guages(-137,239)
		self.cabin = self.Cabin_Pressure_Guages(116,266)
		self.brakes = self.Brake_Temp_Guages(130,78)
		
	def comp(self, aircraft):
		#Do all computes for this guage.
		pass
		#self.show_FANVIB.comp(aircraft.Eng_1, aircraft.Eng_2, aircraft.onground.value, aircraft.global_time)
		#self.show_GEARFLAP.comp(aircraft.flaps, aircraft.gear, aircraft.global_time)
		
	def draw(self, aircraft, x,y):
		
		#Background image flashing for placement assistance.
		#if (globaltime.value % 10) > 5:
		#	self.bg_image.draw(x-255,y+45)
			
		#Compute logic of Guage
		self.comp(aircraft)
		
		glPushMatrix()
		glTranslatef(x,y,0)
		glLineWidth(2.0)
		#Draw Trim Guages
		self.trim.draw(aircraft.trim)
		#Draw APU Guages
		self.APU.draw(aircraft.APU)
		#Draw Cabin Data Guage
		self.cabin.draw()
		self.brakes.draw(aircraft.brakes)
		#glScale(0.12,0.12,1.0)
		#glText("%5.2f %5.2f %5.2f" %(aircraft.trim.Elevator.value, aircraft.trim.Rudder.value, aircraft.trim.Aileron.value))
		#globaltest.draw(-200,30)
				
		glPopMatrix()
