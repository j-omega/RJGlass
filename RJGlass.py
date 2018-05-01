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

#import config #local config.py file in same directory
import time

from guage import * #All add on guage functions colors etc. 
import PFD_mod
import ND_mod
import aircraft #Does all of the aircraft_data
import keyboard #Handles all keyboard commands

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


# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'
# Number of the glut window.
window = 0

class screen(object):
	def __init__(self):
		self.x_s = 1.0
		self.y_s = 1.0
	

# A general OpenGL initialization function.  Sets all of the initial parameters. 
def InitGL(x,y):
	global window
	
	glutInit(())
	
	# Select type of Display mode:   
	#  Double buffer 
	#  RGBA color
	# Alpha components supported 
	# Depth buffer
	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
	
	# get a 800 x 600 window 
	#glutInitWindowSize(800, 600)
	glutInitWindowSize(x,y)
	# the window starts at the upper left corner of the screen 
	glutInitWindowPosition(0, 0)
	
	# Okay, like the C version we retain the window id to use when closing, but for those of you new
	# to Python (like myself), remember this assignment would make the variable local and not global
	# if it weren't for the global declaration at the start of main.
	window = glutCreateWindow("PFD")

	# Register the drawing function with glut, BUT in Python land, at least using PyOpenGL, we need to
	# set the function pointer and invke a function to actually register the callback, otherwise it
	# would be very much like the C version of the code.	
	glutDisplayFunc (DrawWindow)
	
	# Uncomment this line to get full screen.
	glutFullScreen()
	#glutEnterGameMode()
	# When we are doing nothing, redraw the scene.
	glutIdleFunc(DrawWindow)
	
	# Register the function called when our window is resized.
	glutReshapeFunc (resize)
	
	# Register the function called when the keyboard is pressed.  `
	glutKeyboardFunc (keyPressed)

	glClearColor(0.0, 0.0, 0.0, 0.0)	# This Will Clear The Background Color To Black

def InitPyGame():
	glutInit(())
	pygame.init()
	if config.full_screen:
		pygame.display.set_mode((1024,768), DOUBLEBUF|OPENGL|FULLSCREEN)
	else:
		pygame.display.set_mode((1024,768), DOUBLEBUF|OPENGL)
	
		
def resize(w, h):
	#global scissor
	if h==0:
		h=1
	
	InitView(True, w, h)
	#test_x = 1280 / 800.0
	#test_y = 800.0 / 600.0
	
	#glViewport(0, 0, w, h);
	#glMatrixMode(GL_PROJECTION);
	#glLoadIdentity();
	#gluPerspective(60.0, w/ h, 1.0, 20.0)
	#glMatrixMode(GL_MODELVIEW)
	#glLoadIdentity()
	#glTranslatef (0.0, 0.0, -5.0)
	
	#return x_s, y_s

def DrawWindow():
	
	def divider(): #Dividing line between instruments
		glColor(white)
		glLineWidth(2.0)
		glBegin(GL_LINES)
		glVertex2f(512.0, 0.0)
		glVertex2f(512.0, 768.0)
		#glVertex2f(405.0, 0.0)
		#glVertex2f(405.0, 768)
		glEnd()
		
	def draw_nodata(x,y):
		glColor(red)
		glLineWidth(5.0)
		glPushMatrix()
		glTranslatef(x,y,0)
		glScalef(0.4,0.4,1.0)
		glText("NO SIM DATA", 100)
		glPopMatrix()
		
	# Clear The Screen, Set orographic projectiong 2d.
	global count
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
	divider()
	#glTranslate(1.0,0.0,0.0)
	#glPushMatrix()
	#print "PFD", time.time()
	PFD.draw(aircraft_data,250,445)
	#print "ND", time.time()
	ND.draw(aircraft_data,512+256, 400)
	
	#If Nodata is coming from Flight Sim, show on screen
	if aircraft_data.nodata:
		draw_nodata(50,500)
		
	
	#glPopMatrix()
	#  since this is double buffered, swap the buffers to display what just got drawn. 
	glDisable(GL_SCISSOR_TEST) #Disable Scissor test so whole display gets swaped
	#If Nodata is coming from Flight Sim, show on screen
	draw_FPS(20,740, aircraft_data.frame_time)
	
	if aircraft_data.nodata:
		draw_nodata(50,500)
	
	#glutSwapBuffers()
	count = count +1
	
	#aircraft_data.test()
	#aircraft_data.read_UDP()
	#aircraft_data.decode_FSX("0.1,0.1,0.1,0.1,0.1,30.12")
	#aircraft_data.read_FSX_UDP()
def InitView(smooth, width, heigth):
	glLoadIdentity()
	#glOrtho(0,800,0.0,600,-1.0,1.0)
	glOrtho(0,width,0.0,heigth,-1.0,1.0)
	#glMatrixMode(GL_PROJECTION)
	#glLoadIdentity()
	#glViewport(0,0,800,600)
	#gluPerspective(45, 1.0, 0.1, 100.0)
	#glMatrixMode(GL_MODELVIEW)
	#glLoadIdentity()
	#gluLookAt(0.0,0.0,5.0, 0.0,0.0,-1.0, 0.0,1.0,0.0)
	
	#x_s = width/800.0
	#y_s = heigth/600.0
	x_s = width/1024.0
	y_s = heigth/768.0

	glScalef(x_s, y_s, 1.0)
	scissor.x_s = x_s
	scissor.y_s = y_s
	print "RESIZEING", width ,heigth
	if smooth:
		#Enable Smoothing Antianalising
		glEnable(GL_LINE_SMOOTH)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
		
def main(x,y,mode):
	global window
	global starttime
	global count
	s = screen()
	#Initialize Window
	# For now we just pass glutInit one empty argument. I wasn't sure what should or could be passed in (tuple, list, ...)
	# Once I find out the right stuff based on reading the PyOpenGL source, I'll address this.
	#InitGL(x,y)
	InitPyGame()
	InitView(True, x, y) #Argument True if you want smoothing
	# Start Event Processing Engine	
	starttime = time.time() # Used for FPS (Frame Per Second) Calculation
	
	#Set up correct function for selected mode
	if mode==config.TEST: mode_func = aircraft_data.test
	elif mode==config.FSXSP0:
		mode_func = aircraft_data.read_FSX
		aircraft_data.setup_SimConnect(mode)
	elif mode==config.FSXSP1:
		mode_func = aircraft_data.read_FSX
		aircraft_data.setup_SimConnect(mode)
	elif mode==config.FSXSP2: #Not tested yet
		mode_func = aircraft_data.read_FSX
		aircraft_data.setup_SimConnect(mode)
	
		
	else:
		print "ERROR: Mode in config file is not defined"
		sys.exit()
	#aircraft_data.read_FSX_UDP()
	#Setup Keyboard 
	keys = keyboard.keylist()
	#keyboard.setup_lists(aircraft_data)
	keys.setup_lists(aircraft_data)
	#print "Starting first Window Draw"
	#keyboard.setup_lists()
	#Inititalize View
	while not (aircraft_data.quit_flag):
		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
		#print time.time()
		DrawWindow()
		#print "Drew Window"
		pygame.display.flip()
		#print "flip"
		#Do mode
		#print "Mode", time.time()
		mode_func()
		# Check for keypresses
		aircraft_data.globaltime = time.time()
		for event in pygame.event.get():
			print event
			if event.type == KEYDOWN:
				#print event
				keys.pressed(event.key, event.mod, aircraft_data.globaltime)
			elif event.type == KEYUP:
				keys.keyup_event()
				
		#Check to see if button is being held down.
		keys.check_stuckkey(aircraft_data.globaltime)
				
	
# Print message to console, and kick off the main to get it rolling.
global count
#global scissor
scissor.x_s = 1.1 #Just assign these, will be reset later.
scissor.y_s = 1.0
count = 0
print "Hit ESC key to quit."
aircraft_data = aircraft.data()
PFD = PFD_mod.PFD_Guage()
ND = ND_mod.ND_Guage(aircraft_data)
print "Main Loop"
#Run main, and get window size and operation mode from config file. config.py
main(config.window_x, config.window_y, config.mode)
#main(800,600)
#===================
# Shuting Down
#===================

#Print average Frames per second on shutdown
print "FPS ", count / (time.time() - starttime)
#Try to kill the thread if it exists. Closes it down on exit				
if config.mode != config.TEST: #If simconnected connected, kill the thread.
	aircraft_data.kill_SimConnect()
	
