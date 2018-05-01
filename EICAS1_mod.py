#!/usr/bin/env python
# ----------------------------------------------------------
# EICAS1_mod MODULE for GlassCockpit procject RJGlass (Left EICAS screen)
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
from EICAS_guage import * #All add EICAS specific guage functions

class EICAS1_guage(object):
	
	
	class Flaps_Bar_c(object):
		def __init__(self, x,y,width):
			self.x = x
			self.y = y
			self.width = width
			self.tick_heigth = 8
			self.tick_width = 2
		def draw_ticks(self, flap_pos, cur_guage_pos):
			glColor(white)
			glLineWidth(2.0)
			w = self.tick_width
			h = self.tick_heigth
			for i in flap_pos:
				cen_x = self.width * i
				
				#Determine if it should be outlined or solid.
				#if (cur_guage_pos >= i) & (cur_guage_pos > 0) :
				#	glBegin(GL_POLYGON)
				#	glVertex2f(cen_x - w, h)
				#	glVertex2f(cen_x - w, -h)
				#	glVertex2f(cen_x + w, -h)
				#	glVertex2f(cen_x + w, h)
				#	glEnd()
				
				glBegin(GL_LINE_LOOP)
				glVertex2f(cen_x - w, h)
				glVertex2f(cen_x - w, -h)
				glVertex2f(cen_x + w, -h)
				glVertex2f(cen_x + w, h)
				glEnd()
		def draw_bar(self, guage_pos):
			glColor(green)
			glLineWidth(10.0)
			
			if guage_pos > 0.0:
				glBegin(GL_LINE_STRIP)
				glVertex2f(-1,0)
				glVertex2f((1+ self.width) * guage_pos , 0)
				glEnd()
			
		
				
		def draw(self, flaps):
			glPushMatrix()
			glTranslatef(self.x, self.y, 0)
			self.draw_bar(flaps.guage_pos)
			self.draw_ticks(flaps.guage_flap_pos, flaps.guage_pos)
			
			glPopMatrix()
			
	class Flaps_Text_c(object):
		
		def __init__(self, x,y, size= 0.11):
			self.x = x
			self.y = y
			self.size = size
		
		def draw(self, flaps_deg):
			glPushMatrix()
			glTranslatef(self.x,self.y,0)
			glPushMatrix()
			glScalef(self.size,self.size,1.0)
			glColor(white)
			glText("FLAPS",95)
			glColor(green)
			glScalef(1.36,1.36,1.0)
			glText(" %2d" %flaps_deg, 95)
			glPopMatrix()
			glPopMatrix()
		
	class Gear_Disp(object):
		def __init__(self, x,y):
			self.x = x
			self.y = y
			
		
		def draw(self,value):
			glPushMatrix()
			glTranslatef(self.x,self.y,0)
			#Three cases UP Down or Transition (Yellow cross hatch)
			if value == 0: #Gear up
				color = white
				text = "UP"
			elif value >= .99: #Gear down
				color = green
				text = "DN"
			else: #Gear in transition
				color = yellow
				text = "--"
			
			glColor(color)
			#Draw outer box
			w = 26
			h = 17
			glBegin(GL_LINE_LOOP)
			glVertex2f(-w,-h)
			glVertex2f(w,-h)
			glVertex2f(w,h)
			glVertex2f(-w,h)
			glEnd()
			#Draw Text
			if text!="--":
				glPushMatrix()
				glTranslatef(-17,-10,0)
				glScalef(0.2,0.2,1.0)
				glText(text,87)
				glPopMatrix()
			else: #Draw crosshatch

				glBegin(GL_LINES)
				glVertex2f(-w+2,-h)
				glVertex2f(4, h)
				glVertex2f(-4, -h)
				glVertex2f(w-2,h)
				glVertex2f(-w+12,h)
				glVertex2f(-w, h-15)
				glVertex2f(w-12,-h)
				glVertex2f(w, -h+15)
				glEnd()
			glPopMatrix()
		
	class Fuel_Qty_Disp(object):
		def __init__(self, x,y, text_size):
			self.x = x
			self.y = y
			self.size = text_size
			self.metric = config.use_metric_units
			
			
		def draw_fuel_qty_text(self,fuel_tank):
			
			glColor(fuel_tank.EICAS_color)
			glText("%5d" %fuel_tank.EICAS_disp,95)	
			
		
		def draw(self, fuel_tank):
						
			glPushMatrix()
			glTranslatef(self.x,self.y,0)
			glPushMatrix()
			glScalef(self.size,self.size,1.0)
			self.draw_fuel_qty_text(fuel_tank)
			glPopMatrix()
			
			glPopMatrix()
		

	class FanVib_Label_c(object):
		#Unique label with vertical and horizontal Words
		def __init__(self, x,y):
			self.x = x
			self.y = y
			
		def draw(self):
			glPushMatrix()
			glTranslatef(self.x, self.y, 0)
			glScalef(0.12, 0.12, 1.0)
			glColor(white)
			for c in "FAN":
				glText(c, 95)
				glTranslatef(-95, -155,0)
			glTranslatef(-97, -111, 0)
			glText("VIB", 95)
			glPopMatrix()
	
	class FF_Data_c(object):
		def __init__(self, x,y, format):
			self.x = x
			self.y = y
			self.text_format = format
			self.size = 0.15
		def draw(self, value):
			glPushMatrix()
			glTranslatef(self.x, self.y, 0)
			glScalef(self.size,self.size,1.0)
			glColor(green)
			glText(self.text_format %value, 95)
			glPopMatrix()
			
	class OilTemp_Data_c(object):
		def __init__(self, x,y, format, red, yellow):
			self.x = x
			self.y = y
			self.text_format = format
			self.red = red
			self.yellow = yellow
			self.size = 0.15
			
		def check_color(self,value):
			#Check appopriate color for OilTemp
			if value < self.yellow:
				glColor(green)
			elif value >= self.red:
				glColor(red)
			else:
				glColor(yellow)
				
		def draw(self, value):
			glPushMatrix()
			glTranslatef(self.x, self.y, 0)
			glScalef(self.size,self.size, 1.0)
			self.check_color(value)
			glText(self.text_format %value , 95)
			glPopMatrix()
			
	class OilPress_Data_c(object):
		def __init__(self, x,y, format, red, yellow):
			self.x = x
			self.y = y
			self.text_format = format
			self.red = red
			self.yellow = yellow
			self.size = 0.15
			
		def check_color(self,value):
			#Check appopriate color for OilTemp
			if value <= self.red:
				glColor(red)
			elif value <= self.yellow:
				glColor(green)
			else:
				glColor(yellow)
				
		def draw(self, value):
			glPushMatrix()
			glTranslatef(self.x, self.y, 0)
			glScalef(self.size,self.size, 1.0)
			self.check_color(value)
			glText(self.text_format %value , 95)
			glPopMatrix()
	
	def load_texture(self):
			self.bg_image = texture_image('images/EICAS_L.png')	
	
	def __init__(self):
		
		
		
		vert_spacing = 134
		#Create Engine Guages
		radius = 60
		self.Eng_CONST = EICAS_data.Engine_constants()
		self.show_FANVIB = EICAS_data.showFANVIB_c()
		#Eng1 N1 Guage
		self.Eng1_N1 = Dial_Guage(-180,600, 60, 90, 320, 0.0, 100, 0.0,  105, "%3.1f", flash_limit = self.Eng_CONST.N1_Overspeed)
		self.Eng1_N1.bug = N1_bug_c()
		self.Eng1_N1.green_arc = self.Eng1_N1.arc(green, 20, 0, self.Eng_CONST.N1_Overspeed, True, False)
		self.Eng1_N1.red_arc = self.Eng1_N1.arc(red, 5, self.Eng_CONST.N1_Overspeed, 100, False, True)
		#Eng2 N1 Guage
		self.Eng2_N1 = Dial_Guage(-40,600, 60, 90, 320, 0, 100, 0, 105, "%3.1f", flash_limit = self.Eng_CONST.N1_Overspeed)
		self.Eng2_N1.bug = self.Eng1_N1.bug
		self.Eng2_N1.green_arc = self.Eng1_N1.arc(green, 20, 0, self.Eng_CONST.N1_Overspeed, True, False)
		self.Eng2_N1.red_arc = self.Eng1_N1.arc(red, 5, self.Eng_CONST.N1_Overspeed, 100, False, True)
		#Eng1 ITT Guage
		self.Eng1_ITT = Dial_Guage(-180,600-vert_spacing, 60, 90, 320, 0, 900, 0, 1000, "%3d")
		self.Eng1_ITT.green_arc = self.Eng1_ITT.arc(green, 25, 0, self.Eng_CONST.ITT_OverTemp, True, False)
		self.Eng1_ITT.red_arc = self.Eng1_ITT.arc(red, 2,self.Eng_CONST.ITT_OverTemp,self.Eng_CONST.ITT_OverTemp,False, True)
		#Eng2 ITT Guage
		self.Eng2_ITT = Dial_Guage(-40,600-vert_spacing, 60, 90, 320, 0, 900, 0, 1000,"%3d")
		self.Eng2_ITT.green_arc = self.Eng2_ITT.arc(green, 25, 0, self.Eng_CONST.ITT_OverTemp, True, False)
		self.Eng2_ITT.red_arc = self.Eng2_ITT.arc(red, 2,self.Eng_CONST.ITT_OverTemp,self.Eng_CONST.ITT_OverTemp,False, True)
		#Eng1 N2 Guage
		self.Eng1_N2 = Dial_Guage(-180,600-2*vert_spacing, 60, 90,315, 0, 100, 0, 105, "%3.1f")
		self.Eng1_N2.green_arc = self.Eng1_N2.arc(green, 20, 0, self.Eng_CONST.N2_Overspeed, True, False)
		self.Eng1_N2.red_arc = self.Eng1_N2.arc(red, 20, self.Eng_CONST.N2_Overspeed, 100, False, True)
		#Eng2 N2 Guage
		self.Eng2_N2 = Dial_Guage(-40,600-2*vert_spacing, 60, 90, 315, 0, 100, 0, 105, "%3.1f")
		self.Eng2_N2.green_arc = self.Eng2_N2.arc(green, 20, 0, self.Eng_CONST.N2_Overspeed, True, False)
		self.Eng2_N2.red_arc = self.Eng2_N2.arc(red, 20, self.Eng_CONST.N2_Overspeed, 100, False, True)
		#Fuel Flow Data
		self.Eng1_FuelFlow = self.FF_Data_c(-223, 229, "%-5d")
		self.Eng2_FuelFlow = self.FF_Data_c(-78, 229, "%5d")
		#Oil Temp Data
		self.Eng1_OilTemp = self.OilTemp_Data_c(-223, 198, "%-3d", self.Eng_CONST.OilTemp_Red, self.Eng_CONST.OilTemp_Amber)
		self.Eng2_OilTemp = self.OilTemp_Data_c(-78, 198, "%5d", self.Eng_CONST.OilTemp_Red, self.Eng_CONST.OilTemp_Amber)
		#Oil Pressure Data
		self.Eng1_OilPress = self.OilPress_Data_c(-223, 167, "%-3d", self.Eng_CONST.OilPres_Red, self.Eng_CONST.OilPres_Amber)
		self.Eng2_OilPress = self.OilPress_Data_c(-78, 167, "%5d", self.Eng_CONST.OilPres_Red, self.Eng_CONST.OilPres_Amber)
		#Eng1 Oil Pressure Guage
		self.Eng1_OilGuage = Dial_Guage(-155, 105, 55, 210, 330, 0,136, 0, 156, "", True)
		self.Eng1_OilGuage.green_arc = self.Eng1_OilGuage.arc(green, 15, self.Eng_CONST.OilPres_Red, self.Eng_CONST.OilPres_Amber, True, False)
		self.Eng1_OilGuage.amber_arc = self.Eng1_OilGuage.arc(yellow, 15, self.Eng_CONST.OilPres_Amber, 136, True, True)
		self.Eng1_OilGuage.red_arc = self.Eng1_OilGuage.arc(red, 15, 0, self.Eng_CONST.OilPres_Red, True, False)
		
		#Eng2 Oil Pressure Guage
		self.Eng2_OilGuage = Dial_Guage(0, 105, 55, 210, 330, 0,136, 0, 156, "", True)
		self.Eng2_OilGuage.green_arc = self.Eng2_OilGuage.arc(green, 15, self.Eng_CONST.OilPres_Red, self.Eng_CONST.OilPres_Amber, True, False)
		self.Eng2_OilGuage.amber_arc = self.Eng2_OilGuage.arc(yellow, 15, self.Eng_CONST.OilPres_Amber, 136, True, True)
		self.Eng2_OilGuage.red_arc = self.Eng2_OilGuage.arc(red, 15, 0, self.Eng_CONST.OilPres_Red, True, False)

		#Eng1 Fan vibration Guage
		self.Eng1_FanVib = Dial_Guage(-180, 105, 55, 90, 330, 0, 5.2, 0, 5.2, "%3.1f", True)
		self.Eng1_FanVib.green_arc = self.Eng1_FanVib.arc(green, 25, 0, self.Eng_CONST.FANVIB_Yellow, True, False)
		self.Eng1_FanVib.amber_arc = self.Eng1_FanVib.arc(yellow,25, self.Eng_CONST.FANVIB_Yellow, 5.2, True, True)
		
		#Eng2 Fan vibration Guage
		self.Eng2_FanVib = Dial_Guage(-40, 105, 55, 90, 330, 0, 5.2, 0, 5.2, "%3.1f", True)
		self.Eng2_FanVib.green_arc = self.Eng2_FanVib.arc(green, 25, 0, self.Eng_CONST.FANVIB_Yellow, True, False)
		self.Eng2_FanVib.amber_arc = self.Eng2_FanVib.arc(yellow,25, self.Eng_CONST.FANVIB_Yellow, 5.2, True, True)
		


		#Create Engine Labels
		self.N1_Label = Guage_Label(-120, 545 +15, "N1")
		self.ITT_Label = Guage_Label(-127, 545- vert_spacing, "ITT")
		self.N2_Label = Guage_Label(-120, 545- 2*vert_spacing - 5, "N2")
		if config.use_metric_units:
			fuel_flow_text = "FF (KPH)"
		else:
			fuel_flow_text = "FF (PPH)"
		self.FF_Label = Guage_Label(-160, 230, fuel_flow_text)
		self.OilTemp_Label = Guage_Label(-160, 199, "OIL TEMP")
		self.OilPressure_Label = Guage_Label(-165, 168, "OIL PRESS")
		self.FanVib_Label = self.FanVib_Label_c(-118, 125)
		self.temp = 0
		
		#Gear and Flap show calc
		self.show_GEARFLAP = EICAS_data.show_GEARFLAP
		
		#Create GEAR Display
		y= 202
		x = 75
		self.Gear_Label = Guage_Label(x+47, y+25, "GEAR")
		spacing = 70
		self.Gear_Left_Disp = self.Gear_Disp(x, y)
		self.Gear_Nose_Disp = self.Gear_Disp(x+spacing, y)
		self.Gear_Right_Disp = self.Gear_Disp(x+2*spacing, y)
		
		#Create FLAPS Display
		x = 50 
		y= 136
		self.Flaps_Text = self.Flaps_Text_c(x+50, y+17)
		self.Flaps_Bar = self.Flaps_Bar_c(x,y, 190)
		
		#Create FUEL QTY Display
		x = 45
		y = 80
		if config.use_metric_units:
			fuel_text = "FUEL QTY (KGS)"
		else:
			fuel_text = "FUEL QTY (LBS)"
			
		self.Fuel_Qty_Label = Guage_Label(x+24,y+20, fuel_text, 0.11)
		self.Total_Fuel_Label = Guage_Label(x,y-25, "TOTAL FUEL", 0.11)
		self.Fuel_Left_Qty = self.Fuel_Qty_Disp(x-23,y-2, 0.14)
		self.Fuel_Center_Qty = self.Fuel_Qty_Disp(x+55,y-2, 0.14)
		self.Fuel_Right_Qty = self.Fuel_Qty_Disp(x+135,y-2, 0.14)
		self.Fuel_Total_Qty = self.Fuel_Qty_Disp(x+131,y-26, 0.14)
		
	def comp(self, aircraft):
		#Do all computes for this guage.
		
		self.show_FANVIB.comp(aircraft.Eng_1, aircraft.Eng_2, aircraft.onground.value, aircraft.global_time)
		#self.show_GEARFLAP.comp(aircraft.flaps, aircraft.gear, aircraft.global_time)
		
	def draw(self, aircraft, x,y):
		#self.bg_image.draw(x-255,y+32)
		glPushMatrix()
		glTranslatef(x,y,0)
		Eng1 = aircraft.Eng_1
		Eng2 = aircraft.Eng_2
		#Compute logic of Guage
		self.comp(aircraft)
		#Draw Engine Guages
		
		self.Eng1_N1.draw(Eng1.N1.value, globaltime, Eng1.N1_text)
		self.Eng2_N1.draw(Eng2.N1.value, globaltime, Eng2.N1_text)
		self.Eng1_ITT.draw(Eng1.ITT.value)
		self.Eng2_ITT.draw(Eng2.ITT.value)
		self.Eng1_N2.draw(Eng1.N2.value)
		self.Eng2_N2.draw(Eng2.N2.value)
		self.Eng1_FuelFlow.draw(Eng1.Fuel_Flow_disp)
		self.Eng2_FuelFlow.draw(Eng2.Fuel_Flow_disp)
		self.Eng1_OilTemp.draw(Eng1.Oil_Temp.value)
		self.Eng2_OilTemp.draw(Eng2.Oil_Temp.value)
		#Draw OilPressure Text
		self.Eng1_OilPress.draw(Eng1.Oil_Pressure.value)
		self.Eng2_OilPress.draw(Eng2.Oil_Pressure.value)
		#Draw Oil Pressure Guage or Fan Vibration Guage
		if self.show_FANVIB.show:
			#Draw Fan Vibration Guage
			self.Eng1_FanVib.draw(Eng1.Fan_Vibration.value)
			self.Eng2_FanVib.draw(Eng2.Fan_Vibration.value)
			self.FanVib_Label.draw()
		else: #Draw OilGuage
			self.Eng1_OilGuage.draw(Eng1.Oil_Pressure.value)
			self.Eng2_OilGuage.draw(Eng2.Oil_Pressure.value)
		
		
		#Draw Engine Guages Labels
		self.N1_Label.draw()
		self.ITT_Label.draw()
		self.N2_Label.draw()
		self.FF_Label.draw()
		self.OilTemp_Label.draw()
		self.OilPressure_Label.draw()
		
		
		
		if self.show_GEARFLAP.show:
			#Draw GEAR Display
			self.Gear_Label.draw()
			self.Gear_Left_Disp.draw(aircraft.gear.Left.position.value)
			self.Gear_Nose_Disp.draw(aircraft.gear.Nose.position.value)
			self.Gear_Right_Disp.draw(aircraft.gear.Right.position.value)
			#Draw FLAPS Display
			self.Flaps_Text.draw(aircraft.flaps.flap_deg)
			self.Flaps_Bar.draw(aircraft.flaps)
		
		#Draw FUEL QTY DIsplay
		self.Fuel_Qty_Label.draw()
		self.Total_Fuel_Label.draw()
		self.Fuel_Left_Qty.draw(aircraft.fuel.left)
		self.Fuel_Center_Qty.draw(aircraft.fuel.center)
		self.Fuel_Right_Qty.draw(aircraft.fuel.right)
		self.Fuel_Total_Qty.draw(aircraft.fuel.total)
				
		
		#glTranslatef(100,100,0)
		#glScalef(0.14,0.14,1.0)
		#glText("Thr1 %5.2f" %aircraft.Eng_1.Throttle.value)
		#glTranslatef(-800,160, 0)
		#glText("Flaps %5.2f" %aircraft.flaps.pos.value)
		#glTranslatef(-800,160, 0)
		#glText("Guage %5.2f" %aircraft.flaps.guage_pos)
		#glTranslatef(-800,160, 0)
		#glText("Deg %3d" %aircraft.flaps.flap_deg)
		glPopMatrix()
