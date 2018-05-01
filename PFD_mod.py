#!/usr/bin/env python
# ----------------------------------------------------------
# PFD_mod MODULE for GlassCockpit procject RJGlass
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

import time
import sys
import math
from guage import * #All add on guage functions colors etc.

#class scissor(
class PFD_Guage(object):
	
	
	class Speed_Guage:
		
		y_center = 140.0
		x_center = 50.0
		knot_unit = 3.5 #Number of units per knot
			
		def arrow(self):
			#White Arrow
			y = self.y_center
			w = 18.0
			h = 10.0
			point = 50.0 #Point of arrow's X cord
			glColor(white)
			glLineWidth(2.0)
			glBegin(GL_LINE_LOOP)
			glVertex2f(point, y)
			glVertex2f(point + w, y -h)
			glVertex2f(point + w, y +h)
			glEnd()
			glBegin(GL_LINES)
			glVertex2f(point +w, y)
			glVertex2f(point +w + 12.0, y)
			glEnd()
			
		def airspeed_diff(self, difference):
			#Purple Line above or below arrow that shoes accel or decel rate. Forcast 5 seconds ahead??
			if abs(difference) > 1: #If forcasted not difference is less than 2 knots then down't show
				y1 = self.y_center
				y2 = y1 + difference * self.knot_unit
				x1 = self.x_center + 18
				x2 = x1 + 12.0
				glLineWidth(2.0)
				glColor(purple)
				glBegin(GL_LINE_STRIP)
				glVertex2f(x1, y2)
				glVertex2f(x2, y2)
				glVertex2f(x2, y1)
				glEnd()
			
		def V_Speeds(self, air_spd, text_y):
			space = 30.0
			def V_Text(prefix, value, x, y):
				glPushMatrix()
				glTranslatef(x, y, 0.0)
				glPushMatrix()
				glScalef(0.15,0.15,1.0)
				s = prefix + str(value)
				glText(s, 80.0)
				glPopMatrix()
				glPopMatrix()
			glColor(cyan)
			#VT
			V_Text("VT ", air_spd.VT, 5.0, text_y)			
			text_y -= space
			#V2
			V_Text("V2 ", air_spd.V2, 5.0, text_y)			
			text_y -= space
			#VR
			V_Text("VR ", air_spd.VR, 5.0, text_y)			
			text_y -= space
			#V1
			V_Text("V1 ", air_spd.V1, 5.0, text_y)
			#After done reset color to white
			glColor(white)

		def over_speed(self, air_spd):
			def barber_pole(start, finish, dir):
				step = 12 #Determine step between
				x1 = 52
				x2 = 64
				glColor(red)
				glLineWidth(2.0)
				glBegin(GL_LINES)
				glVertex2f(x1, start)
				glVertex2f(x1, finish)
				glVertex2f(x2, start)
				glVertex2f(x2, finish)
				glEnd()
				num = abs((finish - start) // step) + 1
				loc = start
				i =0
				d = step* dir
				while i <= num:
					i+=1
					#Draw polygon
					glBegin(GL_POLYGON)
					glVertex2f(x1, loc)
					glVertex2f(x2, loc)
					loc+=d
					glVertex2f(x2,loc)
					glVertex2f(x1,loc)
					loc+=d
					glEnd()
			
			#Begin over_speed
			unit_apart = self.knot_unit
			y_center = self.y_center
			airspeed = air_spd.IAS_guage
			diff = air_spd.VNE - airspeed
			loc = diff * self.knot_unit 
			if loc <= y_center: 
				barber_pole(loc + y_center, 150 + y_center, 1)
			#Begin under_speed
			diff= air_spd.VS - airspeed
			loc = diff * self.knot_unit
			if loc >= -y_center:
				barber_pole(loc + y_center, -150 + y_center, -1)
		
		def tick_marks(self, air_spd, x, y):


			#Draw the tick mark
			#Every knot is 2.0 units apart
			unit_apart = self.knot_unit
			center = 50.0
			y_center = self.y_center
			#air_spd is class of speed, will use IAS, Mach, and V Speeds, possibly Ground Speed
			airspeed = air_spd.IAS_guage
			#glScissor(5, 152, 80, 300)
			scissor(x, y, 90, 280)
						
			glEnable(GL_SCISSOR_TEST)
			glColor3f(1.0, 1.0, 1.0)
			glLineWidth(2.0)
			start_tick_ten = (int(airspeed) / 10) - 6
			tick_ten = start_tick_ten
			start_loc = y_center - ((airspeed - (tick_ten * 10)) * unit_apart)
			loc = start_loc
			glBegin(GL_LINES)
			vert_line_bottom = -10
			for i in range(13):
			#Tick itself
				if tick_ten == 4:
					vert_line_bottom = loc
				if tick_ten >=4: #This causes nothing below 40 to be displyed
					glVertex2f(center - 10.0, loc)
					glVertex2f(center, loc)
					if tick_ten <20: #If its under 200 knots add a 5 knot mork
						mid_loc = loc + (unit_apart * 5) # This is equivelent of 5 knots higher
						glVertex2f(center - 5.0, mid_loc)
						glVertex2f(center, mid_loc)
				tick_ten = tick_ten +1
				loc = loc + (unit_apart * 10)	
			#Draw verticle Line of airspeed tape
			glVertex2f(center, vert_line_bottom)
			glVertex2f(center, 300.0)
			glEnd()
	
	
			loc = start_loc
			tick_ten = start_tick_ten
			glLineWidth(2.0)
			for i in range(13):
			# Put in numbers
				if (tick_ten >=4) & (tick_ten % 2 == 0): #Must be multiple of 20 and above 0 knots
				#Print out number print
					glPushMatrix()
					if tick_ten >=10:
						glTranslatef(8.0, loc - 6.0, 0.0)
						glScalef(0.13,0.13,1) #Scale text, also done in else statement below.
						c = (tick_ten / 10) + 48
						glutStrokeCharacter(GLUT_STROKE_ROMAN, c)
					else:
						glTranslatef(18.0, loc - 6.0, 0.0) #Move over since no hundreds digit
						glScalef(0.13,0.13,1) #Don't forget to scale text
					c = (tick_ten % 10) + 48
					glutStrokeCharacter(GLUT_STROKE_ROMAN, c) #Tens digit
					glutStrokeCharacter(GLUT_STROKE_ROMAN, 48) # Ones Digit
					glPopMatrix()
				elif (tick_ten == 3): #Put in V Speed Text
					self.V_Speeds(air_spd, loc - 12.0)
				tick_ten = tick_ten +1
				loc = loc + (unit_apart * 10)
				
			
	
		
		def bug_polygon(self):
			glColor(purple)
			glBegin(GL_LINE_LOOP)
			glVertex2f(0.0,0.0)
			glVertex2f(10.0, 8.0)
			glVertex2f(10.0, 15.0)
			glVertex2f(0.0, 15.0)
			glVertex2f(0.0, -15.0)
			glVertex2f(10.0, -15.0)
			glVertex2f(10.0, -8.0)
			glEnd()
		
		
		def airspeed_mach_text(self, value, x, y): # Text on top

			glLineWidth(2.0)
			glColor(white)
			#Draw Text Part
			glPushMatrix()
			glTranslate(x, y, 0.0)
			glScale(0.13,0.13,1.0)
			glText("M", 100)
			glText(("%3.3f" %value)[1:], 90)
			glPopMatrix()
		
		def airspeed_bug_text(self, bug): # Text on top
			glPushMatrix()
			glLineWidth(2.0)
			#Draw Bug Symbol
			glTranslate(10.0, -25.0, 0.0)
			self.bug_polygon()
			glPopMatrix()
			#Draw Text Part
			glPushMatrix()
			glTranslate(30.0, -32.0, 0.0)
			glScale(0.15,0.15,1.0)
			glText(str(bug))
			glPopMatrix()
			
			
	
		def airspeed_bug(self, airspeed): # Also speed on top
			glPushMatrix()
			#Determine bugs position
			diff = airspeed.bug - airspeed.IAS_guage
			#Determine translation amount
			unit_apart = self.knot_unit
			center = self.y_center
			noshow = center + 15.0
			t = diff * unit_apart #2.5 units per knot
			#If its out of bounds dont even draw it.
			if abs(t) <= noshow: 
				glTranslate(52.0, center + t, 0.0) #Move to point of bug center + translation of t
				glLineWidth(2.0)
				self.bug_polygon()
			glPopMatrix()
			
		def Vspeed_bug(self, air_spd): #Puts in the blue marks on speed tape for V-Speeds
		
			def mark_bug(IAS, bug, text):
				
				#IAS current airspeed, bug is bug airspeed text is text to put next to mark
				diff = (IAS - bug) * self.knot_unit
				center = self.y_center
				noshow = center + 5.0 #If out of this range then don't show
				if abs(diff) <= noshow:
					glPushMatrix()
					glTranslate(30.0, center - diff, 0.0) #Move to point of V speed bug
					#Draw Line
					glBegin(GL_LINES)
					glVertex(0.0,0.0)
					glVertex(30.0,0.0)
					glEnd()
					#Draw Text next to line 1,2,R,T
					glTranslate(32.0, -6.0, 0.0)
					glScalef(0.12,0.12,1.0)
					glText(text, 90)
					glPopMatrix()
					
			
			glColor(cyan)
			glLineWidth(2.0)
			mark_bug(air_spd.IAS_guage,air_spd.V1," 1")
			mark_bug(air_spd.IAS_guage,air_spd.V2, " 2")
			mark_bug(air_spd.IAS_guage,air_spd.VR, "R")
			mark_bug(air_spd.IAS_guage,air_spd.VT, "T")
				
			
			
		def draw(self, airspeed, x, y):
		#airspeed is in knots.
		#CRJ - Airspped Guage
		# Location 2,88 to 90,368
		# Start x,y point is top left corner of airspeed tape
			glPushMatrix()
			glTranslatef(x, y, 0.0)
			
			self.tick_marks(airspeed, x, y) #Draw tick marks with numbers
			#self.over_speed(airspeed)
			if airspeed.IAS >40: self.airspeed_diff(airspeed.IAS_diff)
			self.arrow()
			self.Vspeed_bug(airspeed)
			glDisable(GL_SCISSOR_TEST)
			self.airspeed_bug(airspeed)
			self.airspeed_bug_text(airspeed.bug)
			self.airspeed_mach_text(airspeed.mach, 15 , 300)			
			glPopMatrix()
			glPushMatrix()
			
			glPopMatrix()
			
			
	class Attitude_Guage:
		#def __init__(self):
		#	scis = scissor_c(
		def Grnd_Sky(self):
			#Draw Ground and Sky
			glColor3f(0.69, 0.4, 0.0) #Draw Brown Color
			glBegin(GL_QUADS)
			glVertex2f(-250.0, -500.0)
			glVertex2f(250.0, -500.0)
			glVertex2f(250.0, 0.0)
			glVertex2f(-250.0, 0.0)
			glColor3f(0.0, 0.6, 0.8) #Draw Blue Color
			glVertex2f(250.0,0.0)
			glVertex2f(-250.0,0.0)
			glVertex2f(-250.0,500.0)
			glVertex2f(250.0, 500.0)
			glEnd()
		

		def Pitch_Marks(self, pitch, line_width, pixel_per_degree):
			def get_width(pitch):
				x = int(round(pitch / 2.5))
				if x==0:
					w = 115
				elif (x % 4) == 0:
					w = 30
				elif (x % 2) ==0:
					w = 15
				else:
					w = 5
				return w
			
			#Draw the pitch marks
			#Uses pitch to determine which pitch lines need to be drawn
			# Draws current pitch -25 degrees and +25 degrees
			#pixel_per_degree = 7.25
			glColor(white)
			glPushMatrix() #Save matrix state
			glLineWidth(line_width)
			#pitch = pitch * -1
			#Round pitch to nearest 2.5 degrees
			start = round(pitch / 2.5) * 2.5
			start = start - 17.5 # Go down 25 degrees
			glTranslatef(0.0, start * pixel_per_degree, 0.0)
			for i in range(13):
				glBegin(GL_LINES)
				w = get_width(start)
				glVertex2f(w * -1, 0.0)
				glVertex2f(w, 0.0)
				glEnd()
				if (w==30): #Draw number for degrees
					c = int(round(abs(start))) / 10 + 48
					if (c>48): #If greater than 0
						glPushMatrix()
						glTranslatef(30.0, -6.0, 0.0) #Move over to right (Numbers only on right side)
						glPushMatrix()
						glScalef(0.13, 0.13, 1.0) #Scale down for numbers
						glutStrokeCharacter(GLUT_STROKE_ROMAN, c)
						glutStrokeCharacter(GLUT_STROKE_ROMAN, 48)
						glPopMatrix()
						glPopMatrix()
				glTranslatef(0.0, 2.5 * pixel_per_degree, 0.0)
				start = start + 2.5
			glPopMatrix()
		def Center_Mark(self):
			def Rect(side):
				glVertex2f(-side * 106.0, 2.0)
				glVertex2f(-side * 106.0, -2.0)
				glVertex2f(-side * 126.0 , -2.0)
				glVertex2f(-side * 126.0, 2.0)
				
			def V_Shape(side):
				glVertex2f(0,0)
				glVertex2f(side * 40.0, -30.0)
				glVertex2f(side * 80.0, -30.0)
				
			
				
			#Draws center dot and l shaped things off to the side
			#glPushMatrix() No need to push, will do not translating
			#Do black parts
			glColor3f(0.0,0.0,0.0)
			glBegin(GL_POLYGON)
			V_Shape(1)
			glEnd()
			glBegin(GL_POLYGON)
			V_Shape(-1)
			glEnd()
			#Do white parts
			glColor3f(1.0,1.0,1.0)
			glLineWidth(2.5)
			glBegin(GL_LINE_LOOP)
			V_Shape(1)
			glEnd()
			glBegin(GL_LINE_LOOP)
			V_Shape(-1)
			glEnd()
			# Do Rectangles on Either End
			glBegin(GL_LINE_LOOP)
			Rect(1)
			glEnd()
			glBegin(GL_LINE_LOOP)
			Rect(-1)
			glEnd()
			# Do white center line on right side
			glBegin(GL_LINES)
			glVertex2f(155, 0)
			glVertex2f(140, 0)
			glEnd()
		
		def Flight_Director(self): #Draw the flight director
			def draw_V(side):
				glBegin(GL_LINE_STRIP)
				glVertex2f(0,0)
				glVertex2f(side *85, -32.0)
				glVertex2f(side * 100, -22.0)
				glVertex2f(0,0)
				glEnd()
				glBegin(GL_LINE_STRIP)
				glVertex2f(side* 100, -22.0)				
				glVertex2f(side* 100, -40.0)
				glVertex2f(side* 85, -32.0)
				glEnd()
			glColor(purple)
			glLineWidth(3.0)
			draw_V(1)
			draw_V(-1)
						
		
		def Static_Triangle(self): #Static Triangle and Marks on top of Atitude
			radius = 120.0
			glLineWidth(2.5)
			def bank_ticks(dir):
				def short():
					glBegin(GL_LINES)
					glVertex2f(0.0, radius + 12.0)
					glVertex2f(0.0, radius)
					glEnd()
				def long():
					glBegin(GL_LINES)
					glVertex2f(0.0, radius)
					glVertex2f(0.0, radius + 25.0)
					glEnd()
				def triang():
					size = 5.0
					glBegin(GL_LINE_LOOP)
					glVertex2f(0.0, radius)
					glVertex2f(size, radius + size * 2)
					glVertex2f(-size, radius + size * 2)
					glEnd()
				glPushMatrix()
				glRotatef(dir * 10.0, 0.0, 0.0, 1.0)
				short()
				glRotatef(dir * 10.0, 0.0, 0.0, 1.0)
				short()
				glRotatef(dir * 10.0, 0.0, 0.0, 1.0)
				long()
				glRotatef(dir * 15.0, 0.0, 0.0, 1.0)
				triang()
				glRotatef(dir * 15.0, 0.0, 0.0, 1.0)
				long()
				glPopMatrix()
			#Draw Solid Triangle
			glColor3f(1.0, 1.0, 1.0)
			size = 8.0
			glBegin(GL_LINE_LOOP)
			glVertex2f(0.0, radius)
			glVertex2f(size, radius + size * 2)
			glVertex2f(-size, radius + size * 2)
			glEnd()
			bank_ticks(1)
			bank_ticks(-1)
			
			
		def Dynamic_Triangle(self, roll): #Triangle that moves durning turn
			glLineWidth(2.5)
			a = abs(roll)
			radius = 120.0
			size = 8.0
			glColor3f(1.0, 1.0, 1.0)
			if a >= 30:  #Bank Angle check turns yellow if angle too great
				glColor3f(1.0, 1.0, 0.0)
			glBegin(GL_LINE_LOOP)
			glVertex2f(0.0, radius)
			glVertex2f(size, radius - size * 2)
			glVertex2f(-size, radius - size * 2)
			glEnd()
			top = radius - size * 2 -1.0
			glBegin(GL_LINE_LOOP)
			glVertex2f(-size, top)
			glVertex2f(-size, top - 7.0)
			glVertex2f(size, top - 7.0)
			glVertex2f(size, top)
			glEnd()
			if a >=30: #If angle >=30 then fill in solid.
				glBegin(GL_POLYGON)
				glVertex2f(0.0, 102.0)
				glVertex2f(-10.0, 90.0)
				glVertex2f(-10.0, 85.0)
				glVertex2f(10.0, 85.0)
				glVertex2f(10.0, 90.0)
				glEnd()
				
		def Glide_Slope(self, offset, x, y):
			
			def ILS_Diamond(h,w, dir):
				#dir direction of error either 1 or -1
				glBegin(GL_LINE_STRIP)
				h=h*dir
				glVertex2f(-w, 0.0)
				glVertex2f(0.0, h)
				glVertex2f(w, 0.0)
				glEnd()

			max = 127 #max valuke of offset
			scale = 72.0 / max
			w = 10
			seg = 20 #Number of segements drawn for circle
			# Draws Glide_Slope if ILS Active
			# x,y is offset from attitude guage
			glPushMatrix()
			glTranslatef(x,y, 0.0)
			#Draw Center Line
			glLineWidth(2.0)
			glColor(white)
			glBegin(GL_LINES)
			glVertex2f(-w, 0.0)
			glVertex2f(w, 0.0)
			glEnd()
			# Draw Top Circles
			glPushMatrix()
			for m in range(2):
				glTranslate(0.0, 36.0 , 0.0)
				glCircle(w - 5 ,seg)
			glPopMatrix()
			#------
			# Draw Bottom Circles
			glPushMatrix()
			for m in range(2):
				glTranslate(0.0, -36.0 , 0.0)
				glCircle(w - 5 ,seg)
			glPopMatrix()
			#----
			glTranslate(0.0, offset * scale, 0.0)
			glColor(green)
			glLineWidth(3.0)
			if offset > -127: #As long as not on bottom draw top arrow
				ILS_Diamond(w+2, w-2, 1) #On Guage.py file
			if offset < 127: #AS long as not on top draw bottom arrow
				ILS_Diamond(w+2, w-2, -1)
			glPopMatrix()
		def Localizer(self,offset, x, y):
			w = 8
			seg = 20 #Number of segements drawn for circle
			scale = 1
			# Draws Glide_Slope if ILS Active
			# x,y is offset from attitude guage
			glPushMatrix()
			glTranslatef(x,y, 0.0)
			#Draw Center Line
			glLineWidth(2.0)
			glColor(white)
			glBegin(GL_LINES)
			glVertex2f( 0.0, -w)
			glVertex2f(0.0, w)
			glEnd()
			# Draw Top Circles
			glPushMatrix()
			for m in range(2):
				glTranslate(40.0, 0.0 , 0.0)
				glCircle(w - 2 ,seg)
			glPopMatrix()
			#------
			# Draw Bottom Circles
			glPushMatrix()
			for m in range(2):
				glTranslate(-40.0, 0.0 , 0.0)
				glCircle(w - 2 ,seg)
			glPopMatrix()
			#----
			glTranslate(offset * scale, 0.0, 0.0)
			glColor(purple)
			ILS_Diamond(w+2, w-2)
			glPopMatrix()
			
		def Markers(self, marker, frame_time, x, y):
			#if attitude.marker
			def draw_box(w,h,t):
				#Draw Rectangle
				glBegin(GL_LINE_LOOP)
				glVertex2f(0,0)
				glVertex2f(w,0)
				glVertex2f(w,h)
				glVertex2f(0,h)
				glEnd()
				#Draw Text
				glTranslatef(3,3,0) #Move for text
				glScalef(0.13,0.13,1)
				glText(t,105)
				
			w = 33
			h = 20
			glPushMatrix()
			glTranslatef(x,y,0)
			glLineWidth(2.0)
			if marker.on == marker.IM:
				marker.count+=frame_time
				if marker.count > 0.2:
					glColor(white)
					draw_box(w,h,"IM")
					if marker.count > 0.4: marker.count-=0.4
			elif marker.on == marker.MM:
				marker.count+=frame_time
				if marker.count >=1.2: marker.count -=1.2
				num = int(marker.count / 0.2) #Get 0-4 if 0 or 2 flash off, else flash on
				
				if (num == 1) | (num>2): #If thoes numbers draw on
					glColor(yellow)
					draw_box(w,h,"MM")
			elif marker.on == marker.OM:
				marker.count+=frame_time
				if marker.count > 0.5:
					glColor(blue)
					#print frame_time
					draw_box(w,h,"OM")
					if marker.count > 1.0: marker.count-=1.0
				
			glPopMatrix()
			
		#Start of Draw_Atitude
		def draw(self, attitude, r_alt, frame_time, x, y):
			pixel_per_degree = 7.25
			pitch = attitude.pitch
			roll = attitude.bank
			guage_width = 310
			guage_heigth = 290
			#pitch = 0.0
			#roll = 10.0
			glPushMatrix()
			glTranslatef(x,y,0.0) #Moves to appropriate place
			scissor(x - (guage_width // 2), y - (guage_heigth // 2), guage_width, guage_heigth) #Only Draw in Atitude guage area
			glEnable(GL_SCISSOR_TEST)
			glLineWidth(1.0)
			#glTranslatef(175.0, 300.0, 0.0) #Move to Guage
			glPushMatrix()
			glRotate(roll, 0.0, 0.0, 1.0) #Rotate
			glPushMatrix()
			glTranslatef(0.0, pitch * -pixel_per_degree, 0.0)  # Pitch
			self.Grnd_Sky()
			#self.Horizon()
			self.Pitch_Marks(pitch, 2.5, pixel_per_degree) #Pitch and linewidth
			glPopMatrix() #Exit pitch
			self.Dynamic_Triangle(roll)
			glPopMatrix() # Exit Rotation
			self.Center_Mark()
			glLineWidth(2.5)
			self.Static_Triangle()

			if attitude.FD_active: 
				glPushMatrix()
				glRotate(attitude.bank - attitude.FD_bank, 0.0, 0.0, 1.0)
				glPushMatrix()
				glTranslatef(0.0, (attitude.pitch - attitude.FD_pitch) * -pixel_per_degree, 0.0) #Pitch)
				self.Flight_Director()
				glPopMatrix()
				glPopMatrix()
			
			glDisable(GL_SCISSOR_TEST)
			self.Markers(attitude.marker, frame_time, 115, 148) #Draw Outer, Middle, or Inner Marker
			self.Glide_Slope(-attitude.GS, 145, 0)
			#self.Localizer(-50, 0, -120)
			glPopMatrix()
			
			
	class Alt_Guage:
		
		def alt_bug(self, altitude, bug, y_center):
			#Draws putple lines for bug
			def line(y):
				glVertex2f(52, y)
				glVertex2f(94, y)
				
			units_apart = 13.0 / 20
			diff = altitude- bug
			if abs(diff) <= 300: #If farther than that away no need to draw it.
				loc = y_center - (diff * units_apart)
				#Draw two purple lines above and below loc
				y1 = 16
				y2 = 19
				glColor(purple)
				glLineWidth(2.0)
				glBegin(GL_LINES)
				line(loc - y1)
				line(loc - y2)
				line(loc + y1)
				line(loc + y2)
				glEnd()

		def tick_marks(self, altitude):
			
			def white_square():
				glLineWidth(2.0)
				glBegin(GL_POLYGON)
				glVertex2f(-10.0, -3)
				glVertex2f(-4.0, -3)
				glVertex2f(-4.0, 3)
				glVertex2f(-10.0, 3)
				glEnd()
			
			#Draw the tick mark
			#Every 20 ft is 13 units apart
			units_apart = 13.0
			y_center = 150.0
			#altitude = aircraft.altitude
			glColor3f(1.0, 1.0, 1.0)
			glLineWidth(2.0)
			start_tick_ten = (altitude / 20) - 16
			tick_ten = start_tick_ten
			start_loc = y_center - ((altitude - (tick_ten * 20)) * units_apart/ 20)
			#start_loc =0.0
			loc = start_loc
			glBegin(GL_LINES)
			for i in range(32):
			#Tick itself
				glVertex2f(42.0, loc)
				glVertex2f(50.0, loc)
				tick_ten = tick_ten +1
				loc = loc + 13.0	
			glEnd()
			loc = start_loc
			tick_ten = start_tick_ten
			glLineWidth(1.0)
			for i in range(32):
			# Put in numbers
				if (tick_ten >=-50) & (tick_ten % 5 == 0): #Must be multiple of 200 and above 0 feet
				#Print out number print
					glPushMatrix()
					temp = abs(tick_ten / 5 ) % 10
					#if tick_ten<0: temp = 10 - temp
					h = 16.0
					if temp ==0: #Need to be lines above and below altitude
						glPushMatrix()
						glTranslatef(52.0, loc, 0.0)
						glLineWidth(2.0)
						glBegin(GL_LINES)
						glVertex2f(0.0, h)
						glVertex2f(42.0, h)
						glVertex2f(0.0, -h)
						glVertex2f(42.0, -h)
						glEnd()
						white_square()
						glPopMatrix()
					elif temp ==5: #Need lines above and below 500' marks also
						glPushMatrix()
						glTranslatef(52.0, loc, 0.0)
						glLineWidth(2.0)
						glBegin(GL_LINES)
						glVertex2f(0.0, h)
						glVertex2f(21.0, h)
						glVertex2f(0.0, -h)
						glVertex2f(21.0, -h)
						glEnd()
						white_square()
						glPopMatrix()
						
					glTranslatef(53.0, loc - 8.0, 0.0)
					glLineWidth(2.0)
					glScalef(0.15,0.15,1) #Scale text, also done in else statement below.
					
					s = str(temp) + "00"
					glText(s, 90)
					glPopMatrix()

				tick_ten = tick_ten +1
				loc = loc + 13.0
				
		def thousand_alt_bug(self, altitude, bug, y_center):
			#Draws putple lines for bug
			def line(y):
				glVertex2f(21, y)
				glVertex2f(37, y)
				
			units_apart = 0.13
			diff = altitude- bug
			if abs(diff) <= 1400: #If farther than that away no need to draw it.
				loc = y_center - (diff * units_apart)
				#Draw two purple lines above and below loc
				y1 = 7
				y2 = 11
				glColor(purple)
				glLineWidth(2.0)
				glBegin(GL_LINES)
				line(loc - y1)
				line(loc - y2)
				line(loc + y1)
				line(loc + y2)
				glEnd()
		
		def thousand_tick_marks(self, altitude, y_center):
			alt = altitude % 1000 #Only need the hundreds feet part because it repeats
			#Draw the tick marks
			#Every 100 ft is 13 units apart
			units_apart = 0.13 #13.0 / 100
			black_l = y_center - 30.0
			black_h = y_center + 30.0
			#altitude = aircraft.altitude
			glColor(white)
			glLineWidth(2.0)
			tick = (alt / 500) - 3
			loc = y_center - ((alt - (tick * 500)) * units_apart)

			for i in range(7):
			#Tick itself
				if (tick % 2): #If odd then 500 foot mark make smaller, if even then make larger 1000 foot mark
					glBegin(GL_LINE_LOOP)
					glVertex2f(29.0, loc -3)
					glVertex2f(37.0, loc -3)
					glVertex2f(37.0, loc +3)
					glVertex2f(29.0, loc +3)
					glEnd()
				else:
					glBegin(GL_LINE_LOOP)
					glVertex2f(21.0, loc -3)
					glVertex2f(37.0, loc -3)
					glVertex2f(37.0, loc +3)
					glVertex2f(21.0, loc +3)
					glEnd()
				tick = tick +1
				loc = loc + 65	
			#Draw black plygon over area, therefore these ticks need to be done first, eaiser then doing multiple scissor boxes	
			glColor(black)
			glBegin(GL_POLYGON)
			glVertex2f(20.0, black_l)
			glVertex2f(38.0, black_l)
			glVertex2f(38.0, black_h)
			glVertex2f(20.0, black_h)
			glEnd()
			
		
		def altitude_disp(self, altitude, x, y):
			#altitude = aircraft.altitude
			def background():
				# Background with white outline
				glPushMatrix() 
				glTranslatef(x, y, 0.0) # Move to where point of outline is
				#Draw White Outline suronding alt reading
				glColor3f(1.0, 1.0, 1.0)
				glLineWidth(2.0)
				glBegin(GL_LINE_STRIP)
				glVertex2f(20.0, 30.0)
				glVertex2f(35.0, 30.0)
				glVertex2f(42.0, 18.0)
				glVertex2f(100, 18.0)
				glEnd()
				glBegin(GL_LINE_STRIP)
				glVertex2f(20.0, -30.0)
				glVertex2f(35.0, -30.0)
				glVertex2f(42.0, -18.0)
				glVertex2f(100, -18.0)
				glEnd()
		
			def thousands():  # This does the thousands and ten thousands digit
				alt = altitude
				thou = alt // 1000
				
				def text_out(d): #Just output the text.
					glScalef(0.18, 0.20, 1.0)
					glText("%2d" %d, 90)
				#Check to see if near change in thousand above 900 feet
				alt_1000 = alt % 1000  
				glPushMatrix()
				if thou <0: #negative number no rolling
				#Display yellow NEG in place of number
					glColor(yellow)
					glDisable(GL_SCISSOR_TEST) #Turn off so text will show up
					glTranslatef(28.0, 8.0, 0.0)
					glScalef(0.10, 0.10, 1.0)
					glText("N",0)
					glTranslatef(0.0, -120.0, 0.0)
					glText("E",0)
					glTranslatef(0.0, -120.0, 0.0)
					glText("G",0)
					
				elif (alt_1000 >= 970): # Close to change in thousand will roll digits
					loc = 30 - (1000 - alt_1000) # / 1.0
					if ((thou +1) % 10) > 0: #If both digits aren't changing then don't roll the 10k digit
						if thou >= 10: #This prevents 0 for being drawn in 10k digit spot
							glPushMatrix() #Draw 10k digit in normal place
							glTranslatef(6.0, -10.0, 0.0)
							glScalef(0.18, 0.20, 1.0)
							glText("%d" % (thou // 10))
							glPopMatrix()
						thou = thou % 10 #Change thou to mod 10 so only 1K digit is drawn
						
					glPushMatrix()
					glTranslatef(6.0, 20.0 - loc, 0.0)
					text_out(thou + 1)
					glPopMatrix()
					glTranslatef(6.0, -10.0 - loc, 0.0)
					text_out(thou)
				else: 
					glTranslatef(6.0, -10.0, 0.0)
					text_out(thou)
				
				
				glPopMatrix()
				
			#Main draw function for altitude_display	
			#Draw Background
			glDisable(GL_SCISSOR_TEST)
			background()
			

			glEnable(GL_SCISSOR_TEST)
			scissor(x-10, y-15, 80, 30)
			#Draw thousands digits
			thousands()
			
				
			glPopMatrix() #Altitude_disp

		def radar_disp(self, aag, x, y, notify):
			if (aag < 2500): #If its above 2500 then don't display
				#Determine number to print on atitude display.
				num = aag
				if num >=1000: #Then do multiples of 50
					#round  to multiples of 50.
					num = (num + 25) // 50 * 50
				else: # Do multiples of 10
					num = (num + 5) // 10 * 10
				#Display radar altitude
				if notify: #If DH notify is on then change color to yellow else green (default color)
					glColor(yellow)
				else:
					glColor(green)
				glLineWidth(2.0)
				glPushMatrix()
				glTranslatef(x, y, 0.0) #Move to start of digits
				#Draw Numbers
				glPushMatrix()
				glScalef(0.16,0.16,1.0)
				glText("%4d" %num, 90)
				glPopMatrix() #scale3f
				# Draw FT
				glPushMatrix()
				glTranslatef(65.0, -1.0, 0.0)
				glScalef(0.12,0.12,1.0)
				glText("FT")
				glPopMatrix() #translate
				glPopMatrix() #translate



		def radar_alt(self, aag, pixel_per_foot, y_cent, DH): # Puts mark on tape that show ground.
			
			
			
			def foreground(aag, y_cent): #Draw the correct white lines for foreground
					glColor(white)
					glLineWidth(2.0)
					if aag > 1020:
						h = 30
					else:
						h = 12
					glBegin(GL_LINES)
					glVertex2f(0.0, y_cent + h)
					glVertex2f(20.0, y_cent + h)
					glVertex2f(0.0, y_cent - h)
					glVertex2f(20.0, y_cent - h)
					glEnd()
			
			
			def radar_scale(aag, pixel_per_foot, y_cent, DH):
				
				def tick_line(w,loc): #Just draw the tick line
					glBegin(GL_LINES)
					glVertex2f(0.0, loc)
					glVertex2f(w, loc)
					glEnd()
					
					
				start_tick = (aag // 100) - 3
				start_loc = y_cent - ((aag - (start_tick * 100.0)) * pixel_per_foot)

				loc = start_loc
				tick = int(start_tick) #Makes sure tick is integer for glText1 command below
				w = 6
				fifty_offset = 50 * pixel_per_foot #The fifty foot offset
				if DH.notify:#If DH notifer is on, change color to yellow, insted of default green
					glColor(yellow)
				else: glColor(green)
				glLineWidth(2.0)
				for i in range(7):
					if  (10 > tick > 0):
						tick_line(w,loc) #Draw tick at 100'
						tick_line(w, loc - fifty_offset) # Draw tick at 50' mark below it.
						glPushMatrix()
						glTranslatef(w + 1, loc - 7.0, 0.0)
						glScalef(0.13,0.13,1.0)
						glText1(tick) #Ok since number will only be 1-9
						glPopMatrix()
					elif tick == 10: #Special case to add the 950' mark
						tick_line(w, loc - fifty_offset)
					tick += 1
					loc += 100 * pixel_per_foot
				
			def ground_mark(aag, pixel_per_foot, y_cent):
				loc = y_cent - ((aag) * pixel_per_foot) #Ever 20 feet is 13 units (pixels)
				glColor(yellow)
				glLineWidth(2.0)
				glBegin(GL_LINE_STRIP)
				w = 20.0 #width of yellow cross hatch
				bot_loc = loc - (225 * pixel_per_foot)
				glVertex2f(1.0, bot_loc)
				glVertex2f(1.0, loc) #Draw horizontal top line
				glVertex2f(w, loc)
				glVertex2f(w, bot_loc)
				glEnd()
				glBegin(GL_LINES)
				for i in range(12): #Draw angled verticle lines
					glVertex2f(1.0, loc)
					glVertex2f(w, loc - 13)
					loc -= 13.0
				glEnd()
				
			def DH_bug(diff, pixel_per_foot, y_cent):
				loc = y_cent - ((diff) * pixel_per_foot)
				glColor(cyan)
				glLineWidth(2.0)
				w1,w2 = 5,20
				h = 10
				#Move to correct position
				glPushMatrix()
				glTranslatef(0,loc,0)
				#Draw Rectangle
				glBegin(GL_QUADS)
				glVertex2f(0,h)
				glVertex2f(w1,h)
				glVertex2f(w1, -h)
				glVertex2f(0, -h)
				glEnd()
				#Draw Line
				glBegin(GL_LINES)
				glVertex2f(w1,0)
				glVertex2f(w2,0)
				glEnd()
				glPopMatrix()
				
			def DH_Notifier(x,y):
				glDisable(GL_SCISSOR_TEST)
				glPushMatrix()
				glTranslate(x,y, 0)
				glColor(yellow)
				glScalef(0.2,0.2, 1.0)
				glLineWidth(2.0)
				glText("DH", 100)
				glPopMatrix()
				glEnable(GL_SCISSOR_TEST)
				
			if aag<1300:
				radar_scale(aag, pixel_per_foot, y_cent, DH)
				if aag<=230:
					ground_mark(aag, pixel_per_foot, y_cent)
			foreground(aag,y_cent)
			DH.notify = False #Reset to false, will turn true is meets condition below
			if DH.visible:
				diff = aag-DH.bug
				DH_bug(diff, pixel_per_foot, y_cent)
				if (diff<=0) & (aag>0): #Turn on DH notifier if under DH and not on ground
					DH_Notifier(-80,y_cent+ 35)
					DH.notify = True

			
		def mda_bug(self, alt, MDA, pixel_per_foot, y_cent, frame_time): # Minmum Decision Alt, bug on alt tape
		
			def attitude_notifier(x,y):
				glDisable(GL_SCISSOR_TEST)
				glPushMatrix()
				glColor(yellow)
				glTranslatef(x,y,0)
				glScalef(0.2,0.2,1.0)
				glLineWidth(2.0)
				glText("MDA", 100)
				glPopMatrix()
				glEnable(GL_SCISSOR_TEST)
				
			def draw():
				glColor(cyan)
				glLineWidth(2.0)
				glBegin(GL_LINE_LOOP)
				glVertex2f(0.0,0.0)
				glVertex2f(-8.0, -14.0)
				glVertex2f(-8.0, 14.0)
				glEnd()
				glBegin(GL_LINES)
				glVertex2f(0.0,0.0)
				glVertex2f(40.0, 0.0)
				glEnd()
				
			diff = alt - MDA.bug
			flash_num =20
			if MDA.visible: #Check to see if on / visible
				#Check if need to turn on notifier and flash it
				if diff <=0: # Turn notifier on and due flash logic
					if MDA.flash<flash_num:
						MDA.frame_count-=1
						MDA.notift = True
						if MDA.frame_count <=0:
							MDA.frame_count+= 0.5 / frame_time #1 Second cycle
							MDA.flash+=1
				else: #Turn notifier off
					MDA.notify = False
					MDA.flash =0
				
				if (MDA.flash %2 == 0): #Check to see if not being flashed
					if (abs(diff) < 300): #Check to see if needs to be drawn
						#Draw Altitude MDA Bug
						loc = y_cent - ((diff) * pixel_per_foot) #Ever 20 feet is 13 units (pixels)
						glPushMatrix()
						glTranslate(54.0, loc, 0.0)
						draw()
						glPopMatrix()
					#Draw Notifier on Attitude Display
					if (MDA.flash > 0): #If notifier is on
						attitude_notifier(-80,y_cent + 5)
					
			
		def mda_text(self, value, x,y):
				glColor(cyan)
				glLineWidth(2.0)
				glPushMatrix()
				glTranslatef(x, y, 0.0) #Move to start of digits
				#Draw MDA (character only)
				glPushMatrix()
				glScalef(0.14,0.14,1.0)
				glText("MDA", 100)
				glPopMatrix() #scale3f
				# Draw Thousands digit
				glPushMatrix()
				glTranslatef(70.0, 0.0, 0.0)
				glScalef(0.14,0.14,1.0)
				glText("%d" %(value // 1000), 120)
				glScalef(0.85,0.85,1.0) #Scale digits 85%
				glText("%03d" %(value % 1000), 90)
				glPopMatrix() #translate
				glPopMatrix()
		def dh_text(self, value, x,y):
				glColor(cyan)
				glLineWidth(2.0)
				glPushMatrix()
				glTranslatef(x, y, 0.0) #Move to start of digits
				#Draw DH (character only)
				glPushMatrix()
				glScalef(0.14,0.14,1.0)
				glText(" DH", 100)
				glPopMatrix() #scale3f
				# Draw Thousands digit
				glPushMatrix()
				glTranslatef(70.0, 0.0, 0.0)
				glScalef(0.14,0.14,1.0)
				glText("%d" %(value), 100)
				glPopMatrix() #translate
				glPopMatrix()
		
		
		
		def alt_bug_text(self, bug, x,y):
			glColor(purple)
			glLineWidth(2.0)
			glPushMatrix()
			glTranslatef(x, y, 0.0) #Move to start of digits
			glScalef(0.16,0.16,1.0)
			glText("%2d" %(bug // 1000), 95)
			glScalef(0.85,0.85,1.0) #Scale digits 85%
			glText("%03d" %(bug % 1000), 95)
			glPopMatrix()
			
		def alt_setting_disp(self, setting, x,y):
			glPushMatrix()
			glTranslate(x,y,0)
			glLineWidth(2.0)
			glColor(cyan)
			#Text out setting
			glPushMatrix()
			glScalef(0.14,0.15,0)
			#value = round(setting,2) 
			#value += 0.01
			glText("%5.2f" %setting, 90) #Round it to 2 places after decimal point 0.01 is slight correction. (Rouding Error?)
			glPopMatrix() #Text 29.92
			#Display IN
			glTranslate(58,-1,0) #move for In display
			glScalef(0.12,0.12,0)
			glText("IN",40)
			glPopMatrix()

		def draw(self, altimeter,x, y, frame_time):
			pixel_per_foot = 13 / 20.0
			y_center = 150.0
			glPushMatrix()
			glEnable(GL_SCISSOR_TEST)
			scissor(x, y, 100, 300)
			glTranslate(x, y, 0.0)
			glLineWidth(1.0)
			#self.background()
			self.tick_marks(altimeter.value)
			
			
			if altimeter.MDA.visible: self.mda_bug(altimeter.value, altimeter.MDA, pixel_per_foot, y_center, frame_time)
			self.thousand_alt_bug(altimeter.value, altimeter.bug, y_center)
			self.thousand_tick_marks(altimeter.value, y_center)
			self.alt_bug(altimeter.value, altimeter.bug, y_center)
			self.radar_alt(altimeter.absolute, pixel_per_foot, y_center, altimeter.DH) #Yellow line with slashes beneth.
			glPopMatrix()
			glPushMatrix()
			
			self.altitude_disp(altimeter.value, x, y + 150)
			#print altimeter.value
			glDisable(GL_SCISSOR_TEST)
			
			self.alt_bug_text(altimeter.bug, x + 30 , y + 345)
			self.alt_setting_disp(altimeter.pressure, x+7, y -25)
			self.radar_disp(altimeter.absolute, x -87, y - 20, altimeter.DH.notify)
			if altimeter.MDA.visible: self.mda_text(altimeter.MDA.bug, x-100, y + 323)
			if altimeter.DH.visible: self.dh_text(altimeter.DH.bug, x -100, y + 343)
			glPopMatrix()	

	class VSI_Guage:
		
			def line(y1, y2):
				glBegin(GL_LINES)
				glVertex2f(0.0, y1)
				glVertex2f(0.0, y2)
				glEnd()
				
			def marks(self, radius, small, med, large):
				
				def line(y1, y2):
					glBegin(GL_LINES)
					glVertex2f(0.0, y1)
					glVertex2f(0.0, y2)
					glEnd()
					
				def text(x,y, s):
					glPushMatrix()
					glTranslatef(x,y-6.0,0.0)
					glScalef(0.13, 0.13, 0.0)
					glText(s)
					glPopMatrix()
				
				#Set up lists with degree marks 
				a = [large] *3 + [small] * 4 + [med] + [small] * 4
				size = a + [large] + a[::-1] #Above + large at 0 + reverse of above
				#Now Degrees to rotate
				rot = [15] * 2 + [6] * 20 + [15] *3
				glColor(white)
				glLineWidth(2.0)
				glPushMatrix()
				#Go through all point on list
				for i in range(25):
					line(radius, radius - size[i])
					glRotate(rot[i], 0.0, 0.0, 1.0)
				glPopMatrix()
				
				#Draw text 1,2,4 on top and bottom and appropriate spot
				x1, y1 = -46.0, 70
				x2, y2 = -26.0, 78
				x4, y4 = -6.0, 82
				# 1's
				text(x1,y1, "1")
				text(x1, -y1, "1")
				#2's
				text(x2,y2, "2")
				text(x2, -y2, "2")
				#4's
				text(x4,y4, "4")
				text(x4, -y4, "4")
			
			def pointer(self, radius, VS):
				#Draw Pointer, convert vertical speed to correct angle
				value = abs(VS) #Disregard negative for now.
				#Determine appropriate angle
				if value <=1000: #Linear up to 1000
				#1000 foot mark is at angle 60 degrees
					angle = value / 1000.0 * -60 #make float
				else: #Value above 1000' exp scale
					if value >4500: value=4500 #Put upper limit on guage
					x = (value / 1000.0) - 1.0
					y = (-1.0/6*x*x)+(7.0/6*x)
					#print y
					#y=1 at 2000 foot mark 15deg, y =2 at 4000 ft mark 30deg
					angle = -60 - (y * 15)
				if VS <=0: angle = angle * -1.0 #If VS negative then make angle -
				#Done determining angle
				#Draw Pointer
				#angle =0
				glColor(green)
				glLineWidth(2.0)
				glPushMatrix()
				glRotate(angle, 0.0, 0.0, 1.0)
				glTranslatef(-radius + 10.0, 0.0, 0.0)
				#Draw line and arrow
				glBegin(GL_LINES)
				glVertex2f(40.0, 0.0)
				glVertex2f(0.0, 0.0)
				glEnd()
				glBegin(GL_POLYGON)
				glVertex2f(0.0, 0.0)
				glVertex2f(30.0, 5.0)
				glVertex2f(30.0, -5.0)
				glEnd()
				glPopMatrix()
				
			def text(self, VS):
				#Draw text in center of guage
				glColor(green)
				glPushMatrix()
				glTranslate(-18.0, -6.0, 0.0)
				glScalef(0.13, 0.13, 0.0)
				value = abs(VS / 1000.0)
				glText("%2.1f" %value)
				glPopMatrix()
				
			
			def draw(self, x, y, radius, VS):			
				glPushMatrix()
				glTranslate(x, y, 0.0)
				self.marks(radius, 5, 10, 15)
				self.pointer(radius, VS)
				self.text(VS)
				glPopMatrix()
				

	class HSI_Guage:
			def Heading_Ticks(self,radius, heading):
				
				def HSI_Text(i): #Returns text equivelent of tick mark
					if i == 0:
						return "N"
					elif i== 9:
						return "E"
					elif i== 18:
						return "S"
					elif i== 27:
						return "W"
					else:
						return str(i)
					
				
				glPushMatrix()
				glRotate(heading, 0.0, 0.0, 1.0)
				glLineWidth(2.0)
				glColor(white)
				for i in range(0,36): #Draw tick ever 10 degrees
					#Draw big tick
					glBegin(GL_LINES)
					glVertex2f(0.0, radius)
					glVertex2f(0.0, radius - 20.0)
					glEnd()
					#Draw Number
					if (i % 3) == 0: #Check to see if multiple of 3
						glPushMatrix()
						c = HSI_Text(i)
						if len(c) == 2: #Two digits
							glTranslate(-6.0, 0.0, 0.0)
						glTranslate(-6.0, radius -40.0, 0.0)
						glScalef(0.15, 0.15, 1.0)
						glText(HSI_Text(i))
						glPopMatrix()
					glRotate(-5.0, 0.0, 0.0, 1.0) #Rotate 5 degrees
					#Draw Small tick
					glBegin(GL_LINES)
					glVertex2f(0.0, radius)
					glVertex2f(0.0, radius - 15)
					glEnd()
					glRotate(-5.0, 0.0, 0.0, 1.0) #Rotate 5 degrees
				glPopMatrix()
				
				
			def marks(self,radius):
				#Put all marks around HSI 3 Traingles and 2 lines			
				
				def triangle(radius,w,h):
					glPushMatrix()
					glTranslate(0.0, radius, 0.0)
					glBegin(GL_LINE_LOOP)
					glVertex2f(0.0, 0.0)
					glVertex2f(-w, h)
					glVertex2f(w, h)
					glEnd()
					glPopMatrix()
				
				def line(radius, h):
					glPushMatrix()
					glTranslate(0.0, radius, 0.0)
					glBegin(GL_LINES)
					glVertex2f(0, 0)
					glVertex2f(0, h)
					glEnd()
					glPopMatrix()
				
				glLineWidth(2.0)
				glColor(white)
				glPushMatrix()
				#90 Degree Line
				glRotate(-90.0,0.0, 0, 1.0)
				line(radius + 5, 15)
				# 45 Degree Smaller Triangle
				glRotate(45.0, 0.0, 0, 1.0)
				triangle(radius + 2, 5, 8)
				# Top Large Triangle
				glRotate(45.0,0, 0, 1.0)
				triangle(radius - 2, 9, 15)
				# 45 Degree Smaller Triangle
				glRotate(45.0, 0.0, 0, 1.0)
				triangle(radius + 2, 5, 8)
				#90 Degree Line
				glRotate(45.0,0.0, 0, 1.0)
				line(radius + 5, 15)
			
				glPopMatrix()
				
			def Plane_Figure(self):

				glLineWidth(3.0)
				glBegin(GL_LINES)
				#Fuesalage
				glVertex2f(0.0, 12.0)
				glVertex2f(0.0, -35.0)
				#Wing (Note: Wing is located slightly below center (3pixeles))
				glVertex2f(-25.0, -1.0)
				glVertex2f(25.0, -1.0)
				#Tail
				glVertex2f(-13.0, -28.0)
				glVertex2f(13.0, -28.0)
				glEnd()
			
			def magnetic_track(self, radius, HSI):
				diff = HSI.Mag_Heading - HSI.Mag_Track
				glPushMatrix()
				glRotate(diff,0,0,1.0)
				glTranslate(0,radius-12,0)
				glColor(green)
				glCircle(6,10)
				glPopMatrix()
				
			
			def heading_bug(self, radius, HSI, frame_time):
			#radius = radius of guage, mag = mag heading of plane bug = heading bug value
			#draw_line True if you want purple line drawn from center to bug, (Used when bug's value is changed)
				def bug_polygon():
					glColor(purple)
					glLineWidth(2.0)
					glBegin(GL_LINE_LOOP)
					glVertex2f(0.0,0.0)
					glVertex2f(10.0, 8.0)
					glVertex2f(10.0, 15.0)
					glVertex2f(0.0, 15.0)
					glVertex2f(0.0, -15.0)
					glVertex2f(10.0, -15.0)
					glVertex2f(10.0, -8.0)
					glEnd()
				def text(x,y, bug):
					glPushMatrix()
					glTranslatef(x,y,0)
					glScalef(0.15,0.15,1)
					glText("HDG %03d" %bug, 90)
					glPopMatrix()
				
				#Check for change in heading bug, reset timer is changed
				if HSI.Heading_Bug != HSI.Heading_Bug_prev:
					HSI.Heading_Bug_Timer = 5.0 / frame_time #Calculate number of frames for 5 seconds
					HSI.Heading_Bug_prev = HSI.Heading_Bug
				#diff = is difference between current heading and bug
				diff = HSI.Mag_Heading - HSI.Heading_Bug
				if diff <0: diff+=360 #Make sure diff is between 0 and 360
				glPushMatrix()
				glRotate(diff + 90, 0, 0, 1) #90 degree offset is since bug_polygon above is rotated
				if (HSI.Heading_Bug_Timer >0): #Enable drawing of line
					draw_line=True
					HSI.Heading_Bug_Timer -=1
				else:
					draw_line=False
				
				#Draw dotted line from center to heading bug
				if (draw_line) or (130 < diff < 230): 
				#If diff is between 130 and 230 then line needs to be drawn because spedbug is notshown
					glColor(purple)
					glLineWidth(2.0)
					start = 15.0
					num = 12
					step = (radius - start) / num
					#glLineStipple(1, 0x00FF) Note: Line stipple didn't look right
					#glEnable(GL_LINE_STIPPLE)
					glBegin(GL_LINES)
					for i in range((num / 2) + 1):
						glVertex2f(start, 0.0)
						start += step
						glVertex2f(start, 0.0)
						start += step
					glEnd()
					#glDisable(GL_LINE_STIPPLE)
				#Draw bug_polygon
				
				glTranslatef(radius - 3, 0.0, 0.0)
				bug_polygon()
				glPopMatrix()
				if draw_line: text(-150,157,HSI.Heading_Bug)
				
			def Bearing(self, radius, aircraft):
				def draw(radius, heading, NavAid, num): #Angle is difference from heading type is either 1 or 2
					def line(y1,y2, num):
						w = 8
						glBegin(GL_LINES)
						if num==1:
							glVertex2f(0,y1)
							glVertex2f(0,y2)
						else:
							glVertex2f(w,y1-8) #The -10 correction needed so line meets up with arrow symbol
							glVertex2f(w,y2)
							glVertex2f(-w,y1-8)
							glVertex2f(-w,y2)
						glEnd()
					def arrow(w,h):
						glBegin(GL_LINE_STRIP)
						glVertex2f(-w,-h)
						glVertex2f(0,0)
						glVertex2f(w,-h)
						glEnd()
						
					def draw_text(name, num): #Draw Text and Symbol
						def mini_arrow(num):
							h,w = 14, 7
							ah = 7 #Arrow Heighth
							glPushMatrix()
							glBegin(GL_LINES)
							glVertex2f(0,0)
							glVertex2f(0,h)
							glVertex2f(0,2)
							glVertex2f(w,-ah)
							glVertex2f(0,2)
							glVertex2f(-w,-ah)
							#Now Draw bottom part that is different
							if num==1:
								glVertex2f(0,0)
								glVertex2f(0,-h)
							else:
								lw = 3
								glVertex2f(lw, -lw)
								glVertex2f(lw, -h)
								glVertex2f(-lw, -lw)
								glVertex2f(-lw, -h)
							glEnd()
							glPopMatrix()
							#Done drawing MiniArrow
								
						#Begin draw_text
						glPushMatrix()	
						if num==1:
							glTranslatef(-170, -60, 0)
							glColor(purple)
						else:
							glTranslatef(-170, -95, 0)
							glColor(cyan)
						mini_arrow(num)
						#Draw Text to left of mini arrow
						glTranslatef(-70, -8, 0) #Move over to begginning of text
						glScalef(0.15, 0.15, 1.0)
						glText(name, 90)
						glPopMatrix()
						#Done with draw_text
					
					#Draw if Active (Draw Text always)
					if NavAid.active:
						angle = Check_360(heading - NavAid.bearing)
						glLineWidth(2.0)
						glPushMatrix()
						glRotate(angle,0,0,1)
						if num==1: 
							glColor(purple)
						else:
							glColor(cyan)
						offset= 40 #Radius from center not to draw bearing line
						arrow_point = 72 #Point at which to draw_arrow
						#Bottom Part
						line(-radius+10, -arrow_point, 1)
						glPushMatrix()
						glTranslatef(0.0,-arrow_point, 0.0)
						arrow(15,15)
						glPopMatrix()
						#Line
						line(-arrow_point, -offset, num)
						#Top Part 
						arrow_point +=10 #Move arrow up little to look more realasitic
						line(radius-10, arrow_point, 1)
						glPushMatrix()
						glTranslatef(0.0, arrow_point, 0.0)
						arrow(15,15)
						glPopMatrix()
						line(arrow_point, offset, num)
						glPopMatrix()
					glPushMatrix()
					draw_text(NavAid.name, num)
					glPopMatrix()
				#Computer Bearing1
				HSI = aircraft.HSI
				if HSI.Bearing1 == HSI.VOR:
					draw(radius,aircraft.HSI.Mag_Heading, aircraft.VOR1, 1)
				elif HSI.Bearing1 == HSI.ADF:
					draw(radius, aircraft.HSI.Mag_Heading, aircraft.ADF1, 1)
				elif HSI.Bearing1 == HSI.FMS:
					print "FMS Future"
				else:
					print "ERROR: HSI.Bearing1 Out of Range"
				#Compute Bearing2
				if HSI.Bearing2 == HSI.VOR:
					draw(radius,aircraft.HSI.Mag_Heading, aircraft.VOR2, 2)
				elif HSI.Bearing1 == HSI.ADF:
					draw(radius, aircraft.HSI.Mag_Heading, aircraft.ADF2, 2)
				else:
					print "ERROR: HSI.Bearing2 Out of Range"
				#draw(radius,140,1)
				
				
			def Nav(self, radius, VOR, hdg):
				diff = hdg - VOR.OBS
				if diff <0: diff+=360 #Make sure diff is between 0 and 360
				glPushMatrix()
				glRotate(diff, 0,0, 1)
				glColor(green)
				glLineWidth(2.5)
				#Draw Constant lines
				h = 70
				offset = 6
				#Draw 4 circles
				x, r, seg = 33, 4, 9
				glPushMatrix()
				glTranslatef(x,0,0)
				glCircle(r,seg)
				glTranslatef(x,0,0)
				glCircle(r, seg)
				glTranslatef(-3*x,0,0)
				glCircle(r,seg)
				glTranslatef(-x,0,0)
				glCircle(r, seg)
				#Done with 4 circles
				glPopMatrix() #Done with circles
				glLineWidth(3.0)
				#Draw Top line and arrow
				arrow_w = 10
				arrow_bot = radius - offset - h/2 - 5
				glBegin(GL_LINE_LOOP)
				glVertex2f(0, radius - offset)
				glVertex2f(-arrow_w, arrow_bot)
				glVertex2f(arrow_w, arrow_bot)
				glEnd()
				glBegin(GL_LINES)
				glVertex2f(0, arrow_bot)
				glVertex2f(0, radius - offset - h)
				#Draw bottom line)
				glVertex2f(0, -radius + offset)
				glVertex2f(0, -radius + offset + h)
				glEnd()
				if VOR.active:
					#Draw CDI Line
					cdi_x = VOR.CDI / 127.0 * (x* 2 + r) #x*2+r is max difflection = to outmost point of outer circle				
					glBegin(GL_LINES)
					glVertex2f(cdi_x, -h)
					glVertex2f(cdi_x, h)
					glEnd()
					#Draw To/From Triangle
					offset, w, h = 60, 7, 15
					glBegin(GL_LINE_LOOP)
					if VOR.ToFrom: #If true TO false is FROM
						#Draw To Arrow
						glVertex2f(0, offset)
						glVertex2f(-w, offset - h)
						glVertex2f(w, offset -h)
					else:
						glVertex2f(0, -offset)
						glVertex2f(-w, -offset +h)
						glVertex2f(w, -offset +h)
					glEnd()
				
				#---
				glPopMatrix()
			
			def Nav_text(self, VOR, x, y):
				
				def text_name(name, active, x, y):
					glPushMatrix()
					glTranslatef(x,y,0)
					if active: #If VOR active draw normal text.
						glPushMatrix()
						glColor(green)
						glScalef(0.17, 0.17, 1)
						glText(name, 90)
						glPopMatrix()
					else: #If VOR not active draw text smaller in red with box around it.
						glPushMatrix()
						glColor(red)
						#Draw Box
						glBegin(GL_LINE_LOOP)
						w, h = 60, 20
						glVertex2f(0,0)
						glVertex2f(0, h)
						glVertex2f(w, h)
						glVertex2f(w, 0)
						glEnd()
						#Draw Smaller text							
						glTranslatef(5, 3, 0) #Move text slightly lower and to right
						glScalef(0.13, 0.13, 1)
						glText(name, 100)
						glPopMatrix()
					glPopMatrix()
					
				def text_course(value, x,y):
					glPushMatrix()
					glTranslatef(x,y,0)
					glScalef(0.14, 0.14, 1.0)
					glText("CRS %3d" %value, 85)
					glPopMatrix()
				
				def text_DME(value, active, x, y):
					glPushMatrix()
					glTranslatef(x,y,0)
					#Do large Digit first if active
					if active:
						glPushMatrix()
						glScale(0.15, 0.15, 1.0)
						glText("%2d." %(value // 1), 90)
						glPopMatrix()
						s = "  %d" %((value *10) % 10)
					else:
						s = "---"
					#Now do tenths digit and NM text. If not active then do "-----" NM
					glTranslatef(-4, -0.2,0) #Move to appropriate place
					glPushMatrix()
					glScalef(0.13, 0.13, 1)
					glText(s, 140)
					glText("NM", 90)
					glPopMatrix()
					#----
					glPopMatrix()
					
				def text_ID(value, active, x, y):
					if active:
						glPushMatrix()
						glTranslatef(x,y,0)
						glScalef(0.14, 0.14, 1.0)
						glText(value, 85)
						glPopMatrix()
			#Draw Text to Left 
				glPushMatrix()
				glLineWidth(2.0)
				text_name(VOR.name, VOR.active, x,y)
				glColor(green)
				text_course(VOR.OBS, x,y - 20)
				text_DME(VOR.DME, VOR.active, x+7, y -45)
				text_ID(VOR.ID, VOR.active, x, y-65)
				
				glPopMatrix()
					
			def draw(self, x,y, aircraft):
				glDisable(GL_SCISSOR_TEST)
				radius = 145
				glPushMatrix()
				glTranslate(x,y,0.0)
				glColor(white)
				self.Plane_Figure()
				self.Heading_Ticks(radius, aircraft.HSI.Mag_Heading)
				self.marks(radius)
				self.magnetic_track(radius, aircraft.HSI)
				self.Nav(radius, aircraft.VOR1, aircraft.HSI.Mag_Heading)
				self.Bearing(radius, aircraft)
				self.Nav_text(aircraft.VOR1, -240, 80)
				self.heading_bug(radius, aircraft.HSI, aircraft.frame_time)

				glPopMatrix()
			

	def __init__(self):
		self.speed = self.Speed_Guage()
		self.artifical_horizon = self.Attitude_Guage()
		self.alt_g = self.Alt_Guage()
		self.HSI = self.HSI_Guage()
		self.VSI = self.VSI_Guage()
	def draw(self,aircraft,x,y): #x,y is the xy cordinates of center of PFD guage
		#rint aircraft.autopilot.ias_bug
		self.speed.draw(aircraft.airspeed, x - 248, y - 140)
		self.artifical_horizon.draw(aircraft.attitude,aircraft.altimeter.absolute,aircraft.frame_time, x + 0, y +0)
		self.alt_g.draw(aircraft.altimeter, x + 155, y - 150, aircraft.frame_time)
		
		self.HSI.draw(x, y-330, aircraft) #Just send the whole aircraft object, as lot of data drawn on HSI
		self.VSI.draw(x+ 240, y-305, 70, aircraft.VertSpeed)
		
		
