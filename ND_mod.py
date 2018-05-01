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
import navdata
import formula
import config
#import aircraft

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
				diff = HSI.Mag_Heading.value - HSI.Mag_Track.value
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
				diff = HSI.Mag_Heading.value - HSI.Heading_Bug.value
				if diff <0: diff+=360 #Make sure diff is between 0 and 360
				glPushMatrix()
				glRotate(diff + 90, 0, 0, 1) #90 degree offset is since bug_polygon above is rotated
				if (HSI.Heading_Bug_Timer > globaltime.value): #Enable drawing of line
					draw_line=True
					#HSI.Heading_Bug_Timer -=1
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
					if within_arc: num_dashes = (num/2) #Only do enough to arc
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
				glColor(black)
				glBegin(GL_POLYGON)
				Draw_List(left)
				glEnd()
				glBegin(GL_POLYGON)
				Draw_List(right)
				glEnd()
				
			def Range_Circle(self, small, large, range):
				
				glColor(white)

				glLineWidth(1.0)
				#Small Circle
				glBegin(GL_LINE_STRIP)
				Draw_List(small)
				glEnd()
				#Large Circle
				glLineWidth(2.0)
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
					
			def navaid_text(self, text, x,y):
				#This is used by all navaid drawing function to draw text next to navaid
				# Draw Text next to it
				glTranslatef(x,y,0)
				glPushMatrix()
				glScalef(0.18,0.18,1.0)
				glText(text, 90)
				glPopMatrix()
			
			def draw_WAYPOINT(self, wp):
				#glLineWidth(2.0)
				glBegin(GL_LINE_STRIP)
				Draw_List(self.WAYPOINT_cord)
				glEnd()
				
				self.navaid_text(wp.ID, 20, -10)
				
			def draw_navaid_VOR(self, nav_obj):
				#Function for drawing VOR's only
				glLineWidth(2.0)
				glColor(cyan)
				#Draw navaid
				#VOR Part
				glBegin(GL_LINE_STRIP)
				Draw_List(self.VOR_cord)
				glEnd()
				#Tacan part
				if nav_obj.TACAN:
					glBegin(GL_LINES)
					Draw_List(self.VORTAC_cord)
					glEnd()
				self.navaid_text(nav_obj.ID, 20, -10)
				
			def draw_navaid_NDB(self, nav_obj):
				#Function for drawing only NDB's
				#Draw navaid
				#Inner circle
				glBegin(GL_LINE_STRIP)
				Draw_List(self.NDB_cord)
				glEnd()
				
				self.navaid_text(nav_obj.ID, 15, -10)
				
			def draw_navaid_APT(self, nav_obj):
				#Function for drawing Airtports
				#Draw Oval
				glBegin(GL_LINE_STRIP)
				Draw_List(self.APT_cord)
				glEnd()

				self.navaid_text(nav_obj.ID, 15, -10)
				
			def draw_navaid_FIX(self, nav_obj):
				#Function for drawing Intersections (Fixes)
				#Draw Triangle
				glBegin(GL_LINE_STRIP)
				Draw_List(self.INT_cord)
				glEnd()

				self.navaid_text(nav_obj.ID, 15, -10)

			def drawflightplan(self, flightplan, plane_latlong, true_head, disp_radius, ND_range):
#					def drawfixes(self, navfix, plane_latlong, true_head, disp_radius, ND_range):
				#Draw the flight plan.
				#First draw lines
				xy_array=[] #saves the xy points to draw lines last.
				glLineWidth(2.0)
				glColor(purple)
				draw_range = int(ND_range * 1.1)
				scalefactor = disp_radius / 1.0 / ND_range
				for wp in flightplan.points:
					dist, bearing = formula.dist_bearing(plane_latlong, wp.latlong)
					dist = dist * scalefactor
					n_bearing = (bearing + (360.0-true_head))
					x,y = formula.polar_to_xy(dist,n_bearing)
					xy_array.append((x,y))
					glPushMatrix()
					glTranslate(x,y,0)
					self.draw_WAYPOINT(wp)
					glPopMatrix()
				#xy_array holds points of a	
				glPushMatrix()
				glBegin(GL_LINE_STRIP)
				for l in xy_array:
					glVertex2f(l[0],l[1])
#							draw_func(fix)
				glEnd()
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
				#Calculate WayPoint Shapes
				self.WAYPOINT_cord = List_Waypoint(15, 4)
				self.VOR_cord = List_VOR(12)
				self.VORTAC_cord = List_VORTAC(12, 6)
				self.APT_cord = List_Circle(12, 12)
				self.INT_cord = List_Circle(10,3) #Since only 3 segments looks like triangle
				self.NDB_cord = List_Circle(6, 8)
		
				
			def drawfixes(self, navfix, plane_latlong, true_head, disp_radius, ND_range, total_dis_traveled):
				if navfix.on: #If it aint' on then don't draw anything.
					type = navfix.type
					#Determine which drawing function is  correct for type of navaid
					if (type == navdata.VORL_type) | (type == navdata.VORH_type):
						draw_func=self.draw_navaid_VOR
					elif type == navdata.NDB_type:
						draw_func=self.draw_navaid_NDB
					elif type == navdata.FIX_type:
						draw_func=self.draw_navaid_FIX
					elif type == navdata.APT_type:
						draw_func = self.draw_navaid_APT
					glLineWidth(2.0)
					glColor(cyan)
					draw_range = int(ND_range * 1.1)
					scalefactor = disp_radius / 1.0 / ND_range
					for fix in navfix.visible: #Go through each of the visible indexes and draw them
						#fix = navfix.array[i]
						
						dist, bearing = formula.dist_bearing(plane_latlong, fix.latlong)
						if dist >=(navfix.max_range + 2): 
							navfix.remove_from_visible(fix, total_dis_traveled, plane_latlong[0], plane_latlong[1])
						elif (dist <= draw_range) & (not fix.inFlightplan): #If fix in flight plan do not draw, as it will be drawn twice.
							#if fix.ID == "KFFC": #TESTING PURPOSES ONLY
							#	print fix.ID, dist, bearing, plane_latlong, fix.latlong
							dist = dist * scalefactor
							n_bearing = (bearing + (360.0-true_head))
							
							x,y = formula.polar_to_xy(dist,n_bearing)
							glPushMatrix()
							glTranslatef(x,y,0)
	#						self.draw_navaid(fix)
							draw_func(fix)
							glPopMatrix()
					
					
					
			def draw(self, x,y, aircraft):
				radius = 280 #Radius of outer circle
				LatLong = (aircraft.Latitude.value, aircraft.Longitude.value)
				glEnable(GL_SCISSOR_TEST)
				scissor(x-254,0,508,y+ radius+2) #2 pixels in from each side 
				glPushMatrix()
				glTranslate(x,y,0.0)
				#Start with fixes
				total_dis = aircraft.ND.dis_traveled.total
				self.drawfixes(navdata.VORH, LatLong, aircraft.HSI.True_Heading, radius, aircraft.ND.range.value, total_dis)
				self.drawfixes(navdata.VORL, LatLong, aircraft.HSI.True_Heading, radius, aircraft.ND.range.value, total_dis)
				self.drawfixes(navdata.NDB, LatLong, aircraft.HSI.True_Heading, radius, aircraft.ND.range.value, total_dis)
				self.drawfixes(navdata.FIX, LatLong, aircraft.HSI.True_Heading, radius, aircraft.ND.range.value, total_dis)
				self.drawfixes(navdata.APT, LatLong, aircraft.HSI.True_Heading, radius, aircraft.ND.range.value, total_dis)
				#self.drawflightplan(navdata.flightplan, LatLong, aircraft.HSI.True_Heading, radius, aircraft.ND.range.value)
				self.Black_Background(self.black_bg_cord_L,self.black_bg_cord_R)
				glColor(white)
				self.Plane_Figure()
				glPushMatrix()
				glTranslate(50,50,0)
				glPopMatrix()
				
				self.Range_Circle(self.small_circle_cord, self.large_circle_cord, aircraft.ND.range.value)
				
				scissor(x-254,0,508, 768) #Chack scissor to only to x cord checking
				self.Heading_Ticks(radius, aircraft.HSI.Mag_Heading.value)
				self.magnetic_track(radius, aircraft.HSI)
				#self.Bearing(radius, aircraft)
				self.heading_bug(radius, aircraft.HSI)
				self.Heading_Disp(radius,aircraft.HSI.Mag_Heading.value)
				glPopMatrix()
				glDisable(GL_SCISSOR_TEST)
			

	def init_load(self, navaid, plane):
		count =0
		navaid.visible = []
		range = navaid.max_range
		for i in navaid.array:
			dist_away = formula.dist_latlong_nm(plane, i.latlong)
			i.total_travel_away = dist_away
			if dist_away <= range:
				#navaid.visible.append(count)
				navaid.add_to_visible(i)
				i.total_travel_away = -2 #Negative so it won't be checked.
			#if count<=5:
			#	print navaid.visible
			#	print i.ID, formula.dist_bearing(plane, i.latlong), plane, i.latlong
			count+=1
		navaid.find_closest()
		
	def check_close_navaids(self, dis_traveled, lat, long):
		
		navdata.VORH.check_closest(dis_traveled, lat, long)
		navdata.VORL.check_closest(dis_traveled, lat, long)
		navdata.NDB.check_closest(dis_traveled, lat, long)
		navdata.FIX.check_closest(dis_traveled, lat, long)
		navdata.APT.check_closest(dis_traveled, lat, long)
		
	def reset_navaids(self, lat, long):
		plane = (lat, long)
		
		self.init_load(navdata.VORH, plane)
		self.init_load(navdata.VORL, plane)
		self.init_load(navdata.NDB, plane)
		self.init_load(navdata.FIX, plane)
		self.init_load(navdata.APT, plane)
		
		
	def __init__(self):
		self.name = "ND"
		self.Moving_Map = self.Moving_Map_Guage()
		#Calculate Distance fron all Points
		
		
		
#		for num in navdata.VOR.visible:
#			navobj  = navdata.VOR.array[num]
#			print navobj.ID, navobj.dist_away, navobj.Freq
		
	def initialize(self, aircraft):
		self.reset_navaids(aircraft.Latitude.value, aircraft.Longitude.value)
			
	def draw(self,aircraft,x,y): #x,y is the xy cordinates of center of ND guage
		y+=400
		#rint aircraft.autopilot.ias_bug
		self.Moving_Map.draw(x, y-175, aircraft) #Just send the whole aircraft object, as lot of data drawn on HSI
		#Check for large movement of plane

		if aircraft.ND.dis_traveled.increment >= 10: #If plane move more than 10 miles in one second
			self.reset_navaids(aircraft.Latitude.value, aircraft.Longitude.value)
			aircraft.ND.dis_traveled.reset()
			print "RESET NAVAID PLANE MOVED TOO FAST"
			
		self.check_close_navaids(aircraft.ND.dis_traveled.total, aircraft.Latitude.value, aircraft.Longitude.value)
		
		
