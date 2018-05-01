#!/usr/bin/env python
# ----------------------------------------------------------
# RJGlass Main Program  version 0.2 8/1/07
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
import sys, os
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
from pygame import image
#from PIL import Image

#import config #local config.py file in same directory
import time

from guage import * #All add on guage functions colors etc. 

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


def InitPyGame():
	glutInit(())
	pygame.init()
	if config.full_screen:
		s = pygame.display.set_mode((1024,768), DOUBLEBUF|OPENGL|FULLSCREEN)
	else:
		s = pygame.display.set_mode((1024,768), DOUBLEBUF|OPENGL)
	return s
		
def InitView(smooth, width, heigth):
	glLoadIdentity()
	glOrtho(0,width,0.0,heigth,-1.0,1.0)
	
	x_s = width/1024.0
	y_s = heigth/768.0

	glScalef(x_s, y_s, 1.0)
	scissor.x_s = x_s
	scissor.y_s = y_s
	if smooth:
		#Enable Smoothing Antianalising
		glEnable(GL_LINE_SMOOTH)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
		
	#Clear Screen
	glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
	
	
def DisplaySplash(filename, delay, window_x, window_y):
	#Display needs to be initialized first.
	i = image.load(filename)
	splash_image = bitmap_image(i)
	#Determine the x and y coords to put in center of screen.
	splash_x = (window_x / 2) - (splash_image.w/2)
	splash_y = (window_y /2) - (splash_image.h/2)
	glRasterPos3f(splash_x,splash_y,0)
	glDrawPixels(splash_image.w, splash_image.h, GL_RGBA, GL_UNSIGNED_BYTE, splash_image.tostring)
	pygame.display.flip()
	time.sleep(1)
	
def DrawWindow():
	
	def divider(): #Dividing vertical white line between instruments
		glColor(white)
		glLineWidth(2.0)
		glBegin(GL_LINES)
		glVertex2f(512.0, 0.0)
		glVertex2f(512.0, 768.0)
		glEnd()
		
	def draw_nodata(x,y): #Draw no data text on screen.
		glColor(red)
		glLineWidth(5.0)
		glPushMatrix()
		glTranslatef(x,y,0)
		glScalef(0.4,0.4,1.0)
		glText("NO SIM DATA", 100)
		glPopMatrix()
		
	global count
	divider()
	PFD.draw(aircraft_data,250,445)
	ND.draw(aircraft_data,512+256, 400)
	
	glDisable(GL_SCISSOR_TEST) #Disable any scissoring.
	draw_FPS(20,740, aircraft_data.frame_time)
	#If Nodata is coming from Flight Sim, show on screen
	if aircraft_data.nodata:
		draw_nodata(50,500)
	
	
	count = count +1 #Used for FPS calc
	

	
def main(mode):
	#global window
	global starttime
	global count
	
	
	# Start Event Processing Engine	
	starttime = time.time() # Used for FPS (Frame Per Second) Calculation
	#Set up correct function for selected mode
	mode_func = aircraft_data.get_mode_func(mode)
	#Setup Keyboard 
	keys = keyboard.keylist(aircraft_data)
	#keys.setup_lists(aircraft_data)
	#Inititalize View
	
	while not (aircraft_data.quit_flag):
		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT) #Clear Screen	
		DrawWindow()
		pygame.display.flip() #Update screen
		mode_func() #Run aircraft mode function, to do all teh calaculations etc.
		#Update globaltime
		aircraft_data.globaltime = time.time()
		globaltime.update(time.time())
		# Check for keypresses
		keys.check_events(pygame.event.get(), globaltime.value)		
				
#===========================================================================
#Main program starts here
#===========================================================================
global count
#global scissor
scissor.x_s = 1.1 #Just assign these, will be reset later.
scissor.y_s = 1.0
count = 0
x = config.window_x
y = config.window_y
#Initialize Window
InitPyGame()
InitView(True, x,y) #Argument True if you want smoothing
#Load Splash Screen if enabled
if config.splash:
	DisplaySplash(config.splash_filename, config.splash_delay, x, y)

#Import the rest of the modules here, after splash screen, so loading is done while splash screen is displayed.
import PFD_mod
import ND_mod
import aircraft #Does all of the aircraft_data
import keyboard #Handles all keyboard commands

#Initialize the guages
PFD = PFD_mod.PFD_Guage()
ND = ND_mod.ND_Guage()
aircraft_data = aircraft.data(PFD)
ND.initialize(aircraft_data)

print "Main Loop"
#Run main, and get window size and operation mode from config file. config.py
main(config.mode)
#===================
# Shuting Down
#===================
#Close pygame mixer
pygame.mixer.quit()
#Print average Frames per second on shutdown
print "FPS ", count / (time.time() - starttime)
#Try to kill the thread if it exists. Closes it down on exit				
aircraft_data.AP.quit() #only here to close debugging files if present.
if config.mode != config.TEST: #If simconnected connected, kill the thread.
	aircraft_data.kill_SimConnect()
	
	
