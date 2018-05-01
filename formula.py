#!/usr/bin/env python
# ----------------------------------------------------------
# formula MODULE for GlassCockpit procject RJGlass
# ----------------------------------------------------------
# This module containes functions that are used in computing formulas for great circle routes
# Distances / Bearing between lat long calcs
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


#These formulas are from http://williams.best.vwh.net/avform.htm
#However I changed the formulas to work with the standard of
# N and E being positive, S and W being negative on the latlong

from math import *
import time

def dist_latlong((lat1, lon1), (lat2, lon2)):
	#Note lat lon are in radians
	#Determins the distance between two points
	#Straight from http://williams.best.vwh.net/avform.htm
	#d=acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon1-lon2))
	e = (sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon2-lon1))
	#d = acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon2-lon1))
	if e>1.0: e = 1.0 #Make sure between -1 and 1 before acos function run.
	elif e<-1.0: e= -1.0
	d = acos(e)
	
	#d = acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon2-lon1))

	return d

def dist_latlong_nm((lat1,lon1),(lat2,lon2)):
	#This one returns nm instead of radians
	#Determins the distance between two points
	#Straight from http://williams.best.vwh.net/avform.htm
	#d=acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon1-lon2))
	#print "LAT LONG test"
	#print lat1, lat2, lon2-lon1
	#d = acos(e)
	distance_nm=((180*60)/3.141592654)*dist_latlong((lat1,lon1),(lat2,lon2))
	return distance_nm

def course_latlong((lat1, lon1), (lat2, lon2),d): #Everything is in Radians.
	#IF sin(lon2-lon1)<0  tc1=acos((sin(lat2)-sin(lat1)*cos(d))/(sin(d)*cos(lat1)))    
	#ELSE tc1=2*pi-acos((sin(lat2)-sin(lat1)*cos(d))/(sin(d)*cos(lat1)))    ENDIF 
	if d==0:
		course=0
	else:
		temp = (sin(lat2)-sin(lat1)*cos(d))/(sin(d)*cos(lat1))
		if temp <-1.0: temp = -1.0 #Make sure between -1 and 1 before calling acos(temp)
		elif temp >1.0: temp = 1.0 
		if sin(lon1-lon2)<0:
			course = acos(temp)    
		else:
			course = 2*pi-acos(temp)
	
	return degrees(course)

def dist_bearing((lat1,lon1),(lat2,lon2)):
	d = dist_latlong((lat1,lon1),(lat2,lon2))
	c = course_latlong((lat1,lon1),(lat2,lon2),d)
	distance_nm=((180*60)/3.141592654)*d 
	#course = degrees(c)
	#Return in NM and Degrees
	return distance_nm, c

def polar_to_xy(r, angle): #Degre
	rad = radians(angle)
	x = r * sin(rad)
	y = r * cos(rad)
	
	return x,y

def latlong_to_deg(latlong):
	lat,long = latlong
	return (degrees(lat), degrees(long))

if __name__ == "__main__":
	LAX = (.592539, 2.06647)
	JFK = (.709186, 1.287762)
	plane = latlong_to_rad((41.921700000000001, -84.082499999999996))
	JXN = latlong_to_rad((42.259231, -84.458530999999994))
	print plane, JXN
	v = time.time()
	for i in range(10):
		distance,course = dist_bearing(plane, JXN)
	d = time.time()
	print distance
	print course