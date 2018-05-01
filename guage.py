#!/usr/bin/env python
# ----------------------------------------------------------
# guage MODULE for GlassCockpit procject RJGlass
# ----------------------------------------------------------
# This module containes functions that are used numerous times with in the RJGlass guages
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

import math
#CONSTANTS
c_VOR = 0
c_ADF = 1



class scissor_c(object):
	def __init__(self, x, y, w, h):
		self.x_o = self.x = x
		self.y_o = self.y = y
		self.w_o = self.w_o = w
		self.h_o = self.h_o = h
	def set(self, x_scale, y_scale):
		"Sets the scissor values depending on the scale given"
		self.x = self.x_o * x_scale
		self.y = self.y_o * y_scale
		self.w_o = self.w_o * x_scale
		self.h_o = self.h_o * y_scale
	
def glText(s, space=80): 
	'takes string input and outputs it to OpenGl Enviornment'
	for c in s: # 
		glPushMatrix()
		if c == "1": #If a 1 then move right a little so looks better
			glTranslatef(15.0, 0.0, 0.0)
		elif c == "I": #If a I then move right too
			glTranslatef(30.0, 0.0, 0.0)
			
		if c ==".": 
			s = 35
		else:
			s = space
		glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(c))
		glPopMatrix()
		glTranslatef(s, 0.0, 0.0)

def glText1_1c(x):
	'Text single digit 0-9 only and writes on screen OpenGL'
	#Includes x correction for #1
	if x==1:
		glTranslatef(10.0, 0.0, 0.0)
		
	glutStrokeCharacter(GLUT_STROKE_ROMAN, x +48)

def glText1(x):
	'Text single digit 0-9 only and writes on screen OpenGL'	
	glutStrokeCharacter(GLUT_STROKE_ROMAN, x +48)
	
def glColor(s): #Expects tuple of three elements Change GL Color
	'Changes Color in OpenGL, Expects Tuple of 3 elements'
	glColor3f(s[0],s[1],s[2])
	
#x_s = 1.0
#y_s = 1.0
#Colors
purple = (1.0, 0.0, 1.0)
grey = (0.2, 0.2, 0.3)
white = (1.0, 1.0, 1.0)
black = (0.0, 0.0, 0.0)
blue = (0.0, 0.0, 1.0)
yellow = (1.0, 1.0, 0.0)
green = (0.0, 0.8, 0.0)
earth = (0.69, 0.4, 0.0) #The ground color on attitude indicator
sky = (0.0, 0.6, 0.8) #Sky color for attitude indicator
cyan = (0.0, 1.0, 1.0)
red = (1.0, 0.0, 0.0)
def scissor(x, y, w, h):
	global scissor
	#Used to change Scissor depending on resolution used
	#glScissor(int(round(x * x_s)), int(round(y * y_s)), int(round(w * x_s)), int(round(h * y_s)))
	#x_s = 1
	#y_s = 1
	x_s = scissor.x_s
	y_s = scissor.y_s
	glScissor(x * x_s, y * y_s, w * x_s, h * y_s)
	#print x_s
	
def glCircle(radius, segments):
	step = 2 * math.pi / segments
	glBegin(GL_LINE_STRIP)
	angle = 0.0
	for i in range(segments +1):
		glVertex2f(radius*math.sin(angle),radius*math.cos(angle))
		angle += step
	glEnd()
	
def List_Circle(radius, segments, start_angle = 0, stop_angle = 360):
	#Returns list of points to make circle of given radius and angles
	step = (stop_angle - start_angle) / 1.0 / segments # /1.0 make sure returns float
	Deg_2_Rad = 3.14159265 / 180
	l = [] #Clear List
	angle = start_angle
	for i in range(segments+1):
		rad = angle * Deg_2_Rad #Convert to radians
		x = radius * math.sin(rad)
		y = radius * math.cos(rad)
		l.append([x,y])
		angle+=step
	#After done whole circle return list	
	return l	
	
def Draw_List(l):
	#Draws points of a list in format [[x1,y1],[x2,y2]]
	#glBegin(GL_LINE_STRIP)
	for i in range(len(l)):
		glVertex2f(l[i][0],l[i][1])
		
def Turn_180(d):
	d+=180
	if d>=360: d-=360
	return d
def Check_360(d): #Used to make sure data is within 0-360
	if d<0:
		d+=360
	elif d>=360:
		d-=360
	return d
