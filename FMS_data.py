#!/usr/bin/env python
# ----------------------------------------------------------
# FMS_data MODULE for GlassCockpit procject RJGlass
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


import time
import sys
import math
from guage import * #All add on guage functions colors etc.
import navdata
from  formula import *
import config
import copy
#import aircraft

class FMS_data_c(object):
	#This holds the color, text, and size for FMS line of text.
		
	def __init__(self):
		self.active_FLPN = FLPN_c("ACT","C", self)
		self.mod_FLPN = FLPN_c("MOD","W", self)
		self.flpn = self.active_FLPN
		self.flight_num = '' #String
		
	def set_mod_flpn(self):
		#self.data.set_mod_flpn()
		if self.flpn.text != "MOD":
			#if flpn is allready mod mode do nothing
			self.mod_FLPN = copy.deepcopy(self.active_FLPN)
			self.mod_FLPN.text = "MOD"
			self.mod_FLPN.color_size = "W"
			self.flpn = self.mod_FLPN
		#self.flpn = self.data.mod_FLPN
		#self.flpn.text = "MOD"
	def execute(self):
		if self.flpn.text !="ACT":
			self.active_FLPN = copy.deepcopy(self.mod_FLPN)
			self.active_FLPN.text = "ACT"
			self.active_FLPN.color_size = "C"
			self.flpn = self.active_FLPN
			
	def cancel_mod(self):
		self.flpn = self.active_FLPN
		self.flpn.text = "ACT"
		self.flpn.color_size = "C"
		
	def set_orgin(self, value):
		self.flpn.route.set_orgin(value)
		
	def set_dest(self, value):
		self.flpn.route.set_dest(value)
	
	def set_altn(self, value):
		self.flpn.alt_route.set_dest(value)
		self.flpn.alt_route.set_orgin(self.flpn.route.orgin)
		
	def set_legs(self, legs):
		self.flpn.route.legs = legs
	def legs_maxpage(self):
		temp = len(self.flpn.route.legs)
		return (temp + 3)/ 4 + 1
	
	
class leg_c(object): #The legs

	def __init__(self, to, jetway = None):
		self.fix = to
		self.distance = 0
		self.heading = 0
		#self.lat = self.fix.lat
		#self.long = self.fix.long
		self.jetway = jetway #if none then direct
		
		

class route_c(object): #The route

	def __init__(self, data):
		self.orgin = None
		self.dest = None
		self.dist = None #Distance from orgin to dest in straight line
		self.legs = []
		self.data = data
		
	def print_legs(self):
		for leg in self.legs:
			print leg.ID
			
	def add_fix(self, legs, fix, pos):
		#Check for duplicates
		num_legs = len(legs)
		if pos >= num_legs:
			legs.append(fix)
		else:
			legs = None
		#self.print_legs()
		return legs
		
	def change_fix(self, fix, pos = 9000): #Put at the end by defult.
		found = False
		new_legs = None #If no changes to legs then it will return None
		num_legs = len(self.legs)
		if pos > num_legs:
			pos = num_legs
		#Check for fix first.
		result = navdata.fix_search(fix)
		if len(result) == 1:
			#If only one found
			print "one found"
			#Add fix
			new_legs = self.add_fix(copy.copy(self.legs), result[0], pos)
		
			found = True
		return new_legs
	
	
	def delete_fix(self, pos):
		new_legs = None
		num_legs = len(self.legs)
		if pos < num_legs:
			new_legs = copy.copy(self.legs)
			new_legs.pop(pos)
		
		return new_legs
	
	def get_fix(self, pos):
		if pos >= len(self.legs):
			return None
		else:
			return self.legs[pos]
	
	def set_orgin(self, value):
		self.orgin = value
		self.calc_dis()
	
	def set_dest(self, value):
		self.dest = value
		self.calc_dis()
	
	#def set_altn(self, value):
	#	self.altn = value
	
	def calc_dis(self):
		#Calculated the distance between orgin and dest
		if ((self.orgin != None) & (self.dest != None)):
			self.dist = int(dist_latlong_nm(self.orgin.latlong, self.dest.latlong))
		else:
			self.dist = None
	
		
class FLPN_c(object):
	
	def __init__(self, text, color_size, data):
		self.route = route_c(data)
		self.alt_route = route_c(data)
		self.data = data
		#self.dest = None
		self.flight_num = ''
		#self.altn = ''
		self.dist = None
		self.text = text
		self.color_size = color_size