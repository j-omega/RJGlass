#!/usr/bin/env python
# ----------------------------------------------------------
# FMS_guage MODULE for GlassCockpit procject RJGlass
# ----------------------------------------------------------
# Copyright 2008 Michael LaBrie
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
from pygame import image
import time
import sys
from guage import * #All add on guage functions colors etc.
#import navdata
import config
#import FMS_control
#import aircraft

#class scissor(
		
class display_c(object):
	
			
	def line_draw(self,y, text, color_size): #y is in data
		
		def draw_empty_box():
			glTranslatef(0, -3,0)
			w = 65
			h = 105
			#glLineWidth(1.0)
			glBegin(GL_LINE_LOOP)
			glVertex2f(0,0)
			glVertex2f(w,0)
			glVertex2f(w,h)
			glVertex2f(0,h)
			glEnd()
			
		glPushMatrix()
		glTranslatef(0,-y,0)
		
		for i in range(24): #Everything is 24 long
			glPushMatrix()
			cs = color_size[i]
			c = text[i]
			color = red
			#print "%r" %cs
			if cs.upper() == 'W':
				#print "WHITE"
				color = white
			elif cs.upper() =='C':
				color = cyan
			
			if cs.isupper():
				size = self.large
			else:
				size = self.small
			
			glScalef(size,size,1.0) #Scale it
			glTranslatef(0,-50,0)
			#glColor(line.color[count])
			glColor(color)
			if c == '!':
				draw_empty_box()
			else:
				glText(c, 100)
			glPopMatrix()
			glTranslatef(11,0,0)
			
		glPopMatrix()
			
		
	
	
	def __init__(self):
		self.large = 0.12
		self.small = 0.10
	
	
		
	
	def draw(self, x, y, line_list):
		line_y = [0,20,39,59,78,98,117,137,156,176,195,215,234,253,272]
		glPushMatrix()
		glColor(white)
		
		glTranslatef(x,y,0.0)
		count =0
		for i in line_list:
			self.line_draw(line_y[count],i.text, i.color_size)
			count+=1
		
		glPopMatrix()
		
		
class FMS_guage_c(object):
	
	
		
	def __init__(self):
		
		#Load Background FMS image
		self.name = "FMS"
		self.display = display_c()
		#i = image.load('images/fms.jpg')
		#self.bg_image = bitmap_image(i)
		import FMS_button
		self.buttons = FMS_button.button_list_c()
		
	def load_texture(self):
		self.bg_image = texture_image('images/fms_original.jpg')
		
	def draw_button_area(self):
		glColor(red)
		glLineWidth(1.0)
		for button in self.buttons.list:
			glBegin(GL_LINE_LOOP)
			glVertex2f(button.x1, 768 - button.y1)
			glVertex2f(button.x1, 768 - button.y2)
			glVertex2f(button.x2, 768 - button.y2)
			glVertex2f(button.x2, 768 - button.y1)
			glEnd()
			
	def draw(self, aircraft, x,y):
		glDisable(GL_SCISSOR_TEST)
		x-= self.bg_image.w /2
		x+=15
		#y-= self.bg_image.h /2
		#glRasterPos3f(x,y,0)
		#glDrawPixels(self.bg_image.w, self.bg_image.h, GL_RGBA, GL_UNSIGNED_BYTE, self.bg_image.tostring)
		self.bg_image.draw(x,y)
		#Draw text
		#self.display.draw(x+ 113, y+674)
		self.display.draw(x+ 113, y+678, aircraft.FMS.display.line_list)
		#glColor(red)
		#self.draw_button_area()
		
	def mousepress(self, button, pos,FMS, stuck = False): #Determines what button is pressed on FMS
		if button == 1:
		#x_pos = pos[0]
		#y_pos = pos[1]
		#Function button on top
			found = False
			for b in self.buttons.list:
				if b.check(pos):
					found = True
					print "FMS", b.name, pos
					if (b.name=='CLR') & (stuck):
						name='CLRALL'
					else: 
						name = b.name
					#FMS_control.button_pressed.append(b.name)
					FMS.button_pressed.append(name)
					#if len(b.name) == 1:
					#	self.display.scratchpad.add_char(b.name)
					#if b.name =='CLR':
					#	self.display.scratchpad.clear_one()
			if not found:
				print "NOT FOUND", pos
		
