#!/usr/bin/env python
# ----------------------------------------------------------
# ND_mod MODULE for GlassCockpit procject RJGlass
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


from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import time
import sys
import math
from guage import * #All add on guage functions colors etc.


#class scissor(
class ND_Guage(object):
	
	
	class Moving_Map_Guage:
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
					
				
				angle_width = 60 #This is the +/- Angle width of the guage
				
				glPushMatrix()
				#Determine how far off from 5 degree mark
				diff_from_5 = heading % 5 #This is the offset to rotate the display
				start_angle = diff_from_5 + angle_width
				start_heading = int((heading / 5)) #This format 0 deg = 0 5 deg = 1 10 deg =2 360 deg = 72
				#												Used to make it eaiser to draw ticks
				
				h = -start_angle
				n = start_heading - (angle_width /5) #Move start heaind over the angle_width of guage
				if n<=0: n+=72 #Make sure it stays positive 72 because of unique format
				#Set up line size
				glLineWidth(2.0)
				glColor(white)
				glRotate(start_angle, 0.0, 0.0, 1.0)
				while h<=angle_width:
					#Check to see if long or short tick
					if h>=-angle_width: #Check to see if tick isn't too far to left to be drawn
						#Draw Tick Mark
						#Determine Tick Size
						size = 10
						if (n%2) == 0:
							size = 20
						glBegin(GL_LINES)
						glVertex2f(0.0, radius)
						glVertex2f(0.0, radius + size)
						glEnd()
						#Draw Number
						if (n % 6) == 0: #Check to see if multiple of 3
							glPushMatrix()
							c = HSI_Text(n/2)
							if len(c) == 2: #Two digits
								glTranslate(-6.0, 0.0, 0.0)
							glTranslate(-6.0, radius +25.0, 0.0)
							glScalef(0.15, 0.15, 1.0)
							glText(HSI_Text(n/2))
							glPopMatrix()
					#Done Drawing Tick
					
					glRotate(-5.0, 0.0, 0.0, 1.0) #Rotate 5 degrees
					n+=1 #Move 5 degrees
					if n>=72: n-=72 #Check upper limit
					h+=5 #Move 5 degrees
				glPopMatrix()
				
			
			def Heading_Disp(self, radius, heading):
				#Display on top of guage that shows magnetic heading
				def pointer(): #The shape of the pointer
					#Used twice, once for black background, one for whit outline
					w , h = 35, 40 #total width and heigth
					aw, ah = 8, 10  #Arrow width and heigth
					glVertex2f(-w,h)
					glVertex2f(-w,ah)
					glVertex2f(-aw,ah)
					glVertex2f(0,0) #Center Point
					glVertex2f(aw,ah)
					glVertex2f(w,ah)
					glVertex2f(w,h)
					
				#Move to point of pointer
				glPushMatrix()
				glTranslatef(0,radius + 10, 0)
				
				#First need to draw black background where numbers will go
				glColor(black)
				glLineWidth(1.0)
				glBegin(GL_POLYGON)
				pointer()
				glEnd()
				#Now draw white outline
				glColor(white)
				glLineWidth(2.0)
				glBegin(GL_LINE_STRIP) #No loop as top is not drawn
				pointer()
				glEnd()
				#Draw Text In Middle 
				glTranslatef(-27, 15,0)
				glScalef(0.2, 0.2, 1.0)
				t = round(heading)
				if t>=360: t = 0 #This is needed because 359.6 would round to 360 needs to be 0
				glText("%03d" %t, 100)
				glPopMatrix()
				
			def Plane_Figure(self): #same size plane as HSI

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
				glTranslate(0,radius+8,0)
				glColor(green)
				glCircle(6,10)
				glPopMatrix()
				
			
			def heading_bug(self, radius, HSI):
			#radius = radius of guage, mag = mag heading of plane bug = heading bug value
			#draw_line True if you want purple line drawn from center to bug, (Used when bug's value is changed)
				def bug_polygon():
					glColor(purple)
					glLineWidth(2.0)
					w,h = 20, 18
					aw,ah = 8, 7
					glBegin(GL_LINE_LOOP)
										
					glVertex2f(ah,0.0)
					glVertex2f(h, aw)
					glVertex2f(h, w)
					glVertex2f(0.0, w)
					glVertex2f(0.0, -w)
					glVertex2f(h, -w)
					glVertex2f(h, -aw)


					glEnd()
				
				
				#Uses PFD Heading Bug to check if heading bug changed and reset timer
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
				if (60 <= diff <= 300): #Checks to see if within plus or minus 60 degrees
					within_arc = False
				else:
					within_arc = True
				#Draw dotted line from center to heading bug
				if (draw_line) or (within_arc): 
				#If diff is between 60 and 300 then line needs to be drawn because spedbug is notshown
					glColor(purple)
					glLineWidth(2.0)
					start = 15.0
					num=16 #16 dashes
					step = (radius - start) / num
					#glLineStipple(1, 0x00FF) Note: Line stipple didn't look right
					#glEnable(GL_LINE_STIPPLE)
					glBegin(GL_LINES)
					#Determine number of dashes
					if within_arc: num_dashes = (num/2) +1 #Only do enough to arc
					else:
						num_dashes = (num/2) + 7 #Do plenty past arc so line goes to end of guage
					for i in range(num_dashes):
						glVertex2f(start, 0.0)
						start += step
						glVertex2f(start, 0.0)
						start += step
					glEnd()
					#glDisable(GL_LINE_STIPPLE)
				#Draw bug_polygon
				if (within_arc): #Only Draw bug if plus or minus 60 degrees
					glTranslatef(radius, 0.0, 0.0)
					bug_polygon()
				glPopMatrix()
						
			
			
			def Black_Background(self, left, right):
				#Draws back blackground on curve
				
				#Add two tops coordinates of the polygon
				glColor(cyan)
				glBegin(GL_POLYGON)
				Draw_List(left)
				glEnd()
				glBegin(GL_POLYGON)
				Draw_List(right)
				glEnd()
				
			def Range_Circle(self, small, large, range):
				
				glColor(white)
				glLineWidth(2.0)
				#Small Circle
				glBegin(GL_LINE_STRIP)
				Draw_List(small)
				glEnd()
				#Large Circle
				glBegin(GL_LINE_STRIP)
				Draw_List(large)
				glEnd()
				#Draw Range numbers
				glPushMatrix()
				glTranslatef(-245, 115, 0)
				glScalef(0.15, 0.15, 1.0)
				glText("%d" %(range))
				glPopMatrix()
				glPushMatrix()
				glTranslatef(-140, 45, 0)
				glScalef(0.15, 0.15, 1.0)
				glText("%g" %(range/2.0))
				glPopMatrix()
					
			def __init__(self):
				#Used to calculate circle coordinates only once.
				radius = 280 #radius of inner circle
				x1, x2 = -254, 254
				y= radius +2 #2 pixel buffer on top
				#start_angle = 0
				#end_angle = 360
				self.small_circle_cord= List_Circle(radius /2 , 40, -60, 285)
				self.large_circle_cord = List_Circle(radius, 30, -60, 60)
				#Determine cordinates for black to make lines not be drawn on curved area above heading display
				self.black_bg_cord_L= List_Circle(radius , 15, -65, 0)
				self.black_bg_cord_L.insert(0,[x1,y])
				self.black_bg_cord_L.append([0,y]) #Add center top point
				self.black_bg_cord_R= List_Circle(radius , 15, 65,0)
				self.black_bg_cord_R.insert(0,[x2,y])
				self.black_bg_cord_R.append([0,y]) #Add center top point
				
			def draw(self, x,y, aircraft):
				radius = 280 #Radius of outer circle
				glEnable(GL_SCISSOR_TEST)
				scissor(514,0,508,y+ radius+2) #2 pixels in from each side 
				glPushMatrix()
				glTranslate(x,y,0.0)
				glColor(white)
				self.Plane_Figure()
				self.Range_Circle(self.small_circle_cord, self.large_circle_cord, aircraft.ND.range.value)
				#self.Black_Background(self.black_bg_cord_L,self.black_bg_cord_R)
				scissor(514,0,508, 768) #Chack scissor to only to x cord checking
				self.Heading_Ticks(radius, aircraft.HSI.Mag_Heading)
				self.magnetic_track(radius, aircraft.HSI)
				#self.Bearing(radius, aircraft)
				self.heading_bug(radius, aircraft.HSI)
				self.Heading_Disp(radius,aircraft.HSI.Mag_Heading)
				glPopMatrix()
			

	def __init__(self):
		self.Moving_Map = self.Moving_Map_Guage()

	def draw(self,aircraft,x,y): #x,y is the xy cordinates of center of ND guage
		#rint aircraft.autopilot.ias_bug
		self.Moving_Map.draw(x, y-175, aircraft) #Just send the whole aircraft object, as lot of data drawn on HSI
		
		
		
