#!/usr/bin/env python
# ----------------------------------------------------------
# EICAS_guage MODULE for GlassCockpit procject RJGlass 
# Holds commond calsses for EICAS screens.
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
			
class N1_bug_c(object):
	#This is only used for the bugs on N1, both circle in V.
		def __init__(self):
			self.active = False
			self.color = cyan
			self.caret = [[-3, -7],[0,0],[3, -7]]
			self.doughnut = List_Circle(5,8) 
				
		def draw(self, radius, angle):
			glColor(self.color)
			glPushMatrix()
			glRotate(-angle,0,0,1)
			glTranslatef(0,radius, 0)
			glBegin(GL_LINE_STRIP)
			Draw_List(self.caret)
			glEnd()
			glPopMatrix()

		
					
class Dial_Guage(object):
	
	def __init__(self, x,y, radius, min_angle, max_angle, min_guage, max_guage, min_display, max_display, text_format, line_arrow = False, flash_limit = None):
		self.x = x
		self.y = y
		self.text_x = 0
		self.text_y = 0
		self.max = max_guage
		self.min = min_guage
		if flash_limit != None:
			self.flash = flash_c(1,4)
			self.flash_limit = flash_limit
		else:
			self.flash = None
			
		self.max_display = max_display
		self.min_display = min_display
		self.angle_max = max_angle
		self.angle_min = min_angle
#			self.green_arc = arcs_c(green, List_Circle(radius, 20, 90, 90+self.angle_max, True, True, radius - 5))
#			self.red_arc = arcs_c(red, List_Circle(radius,3, 340,355, True, True, radius -5))
		self.green_arc = arcs_c(black) #Make arcs blank for now
		self.red_arc = arcs_c(black) 
		self.amber_arc = arcs_c(black)
		self.radius = radius
		self.tick_radius = radius - 7
		self.text_format = text_format
		self.bug = None #Only used on N1 Guage
		if line_arrow == True:
			self.draw_arrow = self.line_arrow
		else:
			self.draw_arrow = self.full_arrow
		
	def calc_angle(self, value):	
		if value < self.min:
			value = self.min
		elif value > self.max:
			value = self.max
		angle = (self.angle_max - self.angle_min)* (1.0 * value / (self.max-self.min) + self.min) + self.angle_min
		
		return angle
	
	def get_color(self, value):
		color = green
		if self.amber_arc.active:
			if self.amber_arc.within(value):
				color = yellow
		if self.red_arc.active:
			if self.red_arc.within(value):
				color = red
		return color
	def arc(self, color, segments, start_value, stop_value, start_tick, stop_tick):
		
		start_angle = self.calc_angle(start_value)
		stop_angle = self.calc_angle(stop_value)
		
		return arcs_c(color, start_angle, stop_angle, List_Circle(self.radius, segments, start_angle, stop_angle, start_tick, stop_tick, self.tick_radius))
	
	
	def full_arrow(self, angle):
		#Green Arrow
		glPushMatrix()
		#angle = self.angle_max * (1.0 * value / self.max) + 90
		#print self.angle_max, value, self.max, angle
		glRotatef(-angle, 0,0,1)
		arrow_w = 5.0
		arrow_h = self.radius - 7
		body_w = 2.0
		body_h = self.radius - 18
					
		glLineWidth(2.0)
		glBegin(GL_LINE_STRIP)
		glVertex2f(body_w,0)
		glVertex2f(body_w,body_h)
		glVertex2f(arrow_w,body_h)
		glVertex2f(0,arrow_h)
		glVertex2f(-arrow_w,body_h)
		glVertex2f(-body_w, body_h)
		glVertex2f(-body_w, 0)
		glEnd()
		glPopMatrix()
		
	def line_arrow(self, angle):
		#Nice Line Arrow - For FAN VIB and Oil Pressure
		glPushMatrix()
		glRotate(-angle,0,0,1)
		glLineWidth(2.0)
		glBegin(GL_LINE_STRIP)
		glVertex2f(0,0)
		glVertex2f(0, self.radius - 7)
		glEnd()
		glPopMatrix()
		
	def draw_arc(self):
		self.green_arc.draw()
		self.red_arc.draw()
		self.amber_arc.draw()

	
	def draw_text(self, value):
		if self.text_format !="":
			if value> self.max_display:
				value = self.max_display
			elif value < self.min_display:
				value = self.min_display
			glPushMatrix()
			glTranslatef(self.text_x, self.text_y,0)
			#If no decimal point shit over slightly to right ex. ITT
			if "d" in self.text_format: 
				glTranslatef(12,0,0)
			
			text = self.text_format %value
			glScalef(0.18,0.18,1.0)
			glText(text, 97)
			glPopMatrix()
	
	def check_flash(self, value):
		
		if self.flash == None:
			return False
		elif value >= self.flash_limit:
			if (self.flash.overflow == False) & (self.flash.active == False):
				self.flash.start()
			return self.flash.flash()
		else:
			self.flash.stop()
			return False
		
	
	def draw(self, value, globaltime = 0, text= None):
		glLineWidth(2.0)
		angle = self.calc_angle(value)
		#if self.flash !=None:
		flash = self.check_flash(value)
			
		glPushMatrix()
		glTranslatef(self.x, self.y, 0.0)
		
		if self.bug != None:
			self.bug.draw(self.radius, self.calc_angle(82.0))
		self.draw_arc()
		glColor(self.get_color(angle))
		if not flash:
			self.draw_arrow(angle)
			glTranslatef(0,22,0)
			self.draw_text(value)
		if text: #POSSIBLY NOT USED
			glTranslatef(-18,-60,0)
			glScalef(0.14,0.14,1.0)
			glText(text, 95)
		
		glPopMatrix()
		
		

	
