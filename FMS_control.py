#!/usr/bin/env python
# ----------------------------------------------------------
# FMS_control MODULE for GlassCockpit procject RJGlass
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
import formula
import config
import pickle
import struct
import FMS_data
import copy
#import aircraft

class text_line_c(object):
	#This holds the color, text, and size for FMS line of text.
		
	def __init__(self,y):
		self.text = ' ' * 24 
		self.color_size = 'W' * 24
		#self.size = ['W'] * 24
		#self.changed = True #Won't re draw line unless its changed.
		#self.y = y
		
	def TCP_data(self):
		o = ''
		for i in self.text:
			o+=i
		for i in self.color_size:
			o+=i
		#o+=struct.pack("I", self.y)
		return o
	
	def clear_text(self):
		self.text = ' ' * 24
		
	def add_text(self, loc, value, color_size):
		pos = loc
		width = len(value)
		#for c in value:
		#	self.text[pos]= c
		#	self.color_size[pos] = color_size
		#	pos+=1
		cs = color_size * width
		self.text = self.text[:loc] + value + self.text[loc+width:]
		self.color_size = self.color_size[:loc] + cs + self.color_size[loc+width:]
		
			
	def add_text_rjust(self, loc, value, color_size, length = None):
		if length != None:
			value = value.rjust(length)
		width = len(value)
		pos = loc - width +1
		cs = color_size * width
		#for c in value:
		#	self.text[pos]= c
		#	self.color_size[pos] = color_size
		#	pos+=1
		self.text = self.text[:pos] + value + self.text[pos+width:]
		self.color_size = self.color_size[:pos] + cs + self.color_size[pos+width:]
		
		
	def remove_text(self, loc, len):
		pos = loc
		s = ' ' * len
		#for i in range(loc, len+loc):
	#		self.text[i] = ' '	
		self.text = self.text[:loc] + s + self.text[loc+len:]	
			
class scratchpad_c(object):
	def __init__(self, text_line, large):
		self.text_line = text_line
		self.large = large
		self.clear_all()
		
	def clear_all(self):
		self.value = ''
		self.text_disp = ''
		self.update_disp()
		
	def delete(self):
		self.text_disp = 'DELETE'
		self.value = '@' #This symbol means delete
		self.update_disp()
		
	def clear_one(self):
		if len(self.value) > 0:
			self.value = self.value[:-1]
			self.text_disp = self.value
			self.update_disp()
	def add_char(self, char):
		if len(self.value)<22:
			self.value = self.value + char
			self.text_disp = self.value
			self.update_disp()
	def invalid_entry(self):
		s = ' '*5 + 'INVALID ENTRY'
		self.set(s, True)
	def set(self, s, disp_only = False): 
		#If disp_only = True then value is cleared.
		if not disp_only:
			self.value = s
		self.text_disp = s
		self.update_disp()
	
	def update_disp(self):
		self.text_line.clear_text()
		self.text_line.add_text(0,'[', "C")
		self.text_line.add_text(23,']', "C")
		self.text_line.add_text(1,self.text_disp, "W")
	def isempty(self):
		if self.value == '':
			print self.value
			return True
		else:
			return False
		
class display_c(object):
	
	def __init__(self):
		self.large = 0.12
		self.small = 0.10
		y_step = 39
		y_step2 = 19
		upper_offset = -19
		self.empty_box = '!' #Special character for empty box shape.
		self.main=[]
		self.upper=[]
		self.line_list=[]
		self.header = text_line_c(0)
		self.line_list.append(self.header)
		y = 0
		for i in range(6):
			y += y_step 
			m = text_line_c(y)
			u = text_line_c(y+upper_offset)
			self.main.append(m)
			self.upper.append(u)
			self.line_list.append(u)
			self.line_list.append(m)
		y+=y_step2
		self.scratch_disp = text_line_c(y)
		self.scratchpad = scratchpad_c(self.scratch_disp, self.large)
		self.line_list.append(self.scratch_disp)
		#self.clear_scratchpad()
		y+=y_step2
		self.message = text_line_c(y)
		self.line_list.append(self.message)
		#Set up functional keys
		self.L0 = func_disp_c('L0',self)
		self.L1 = func_disp_c('L1',self)
		self.L2 = func_disp_c('L2',self)
		self.L3 = func_disp_c('L3',self)
		self.L4 = func_disp_c('L4',self)
		self.L5 = func_disp_c('L5',self)
		self.R0 = func_disp_c('R0',self)
		self.R1 = func_disp_c('R1',self)
		self.R2 = func_disp_c('R2',self)
		self.R3 = func_disp_c('R3',self)
		self.R4 = func_disp_c('R4',self)
		self.R5 = func_disp_c('R5',self)
		
	def get_TCP_send(self):
		o = ''
		for i in self.line_list:
			o+=i.TCP_data()
		
		return o
		
	
	def clear_display(self):
		for line in self.main:
			line.clear_text()
		for line in self.upper:
			line.clear_text()
	
class func_disp_c(object):
	def p(self, value, button):
		pass
	def isblank(self):
		r = False
		if ((self.value == '') | (self.value == '!') | (self.value == '-')):
			r = True
		return r
	
	def set_func(self, func, send_blank = False):
		if func == None:
			self.func = self.p
		else:
			self.func = func
		self.send_blank = send_blank
	
	def __init__(self, name, display):
		self.value = ''
		self.display = display
		self.name = name
		self.func = self.p
		self.send_blank = False 
			#Some functions need to send data even if scratchpad is blank
			#If set to true self.func will still be called even if scratchpad is blank
	def pressed(self):
		if self.display.scratchpad.isempty():
			if self.send_blank: #Also disable setting value from the scratchpad
					self.func('', self)
			elif not self.isblank():
				self.display.scratchpad.set(self.value)
				print "SCRATCH", self.value
			
		else: #Scratchpad is not empty
			self.func(self.display.scratchpad.value, self) #Send value of scratchpad and button name
					
class FMS_c(object):
	
	def __init__(self, aircraft):
		self.data = FMS_data.FMS_data_c()
		#Load Background FMS image
		self.display = display_c()
		self.aircraft = aircraft
		self.ACT_FPLN_page = ACT_FPLN(self.display, self.aircraft, self.data)
		
		self.page = self.ACT_FPLN_page
		self.page.selected()
		self.button_pressed = [] # A list of buttons that have been pressed and have to be processed
		#self.get_TCPsend()
		#self.get_Pickle()
	
	def get_TCPsend(self):
		
		#def convert_text_linc
		o = self.display.get_TCP_send()
		len_o = struct.pack("i", len(o))
		s = "FMS%s%s" %(len_o, o)
		print "%r" %s
		print "LENGTH" ,len(s)
		return s
	def get_Pickle(self):
		o = pickle.dumps(self.display.line_list, -1)
		len_o = struct.pack("i", len(o))
		s = "FMS%s%s" %(len_o, o)
		print "%r" %s
		print "LENGTH" ,len(s)
		return s
	def check_buttons(self):
		if config.mode != config.CLIENT:
			#Server mode process key pressed
			if len(self.button_pressed) > 0:
				self.process_button(self.button_pressed.pop(0))
			#If in client mode, then this list will be poped by Client sending the 
			#key code to server.
			
	def process_button(self, button):
		if len(button) == 1:
			self.display.scratchpad.add_char(button)
		elif button == "CLR":
			self.display.scratchpad.clear_one()
		elif button == "CLRALL":
			self.display.scratchpad.clear_all()
		elif button == "DEL":
			self.display.scratchpad.delete()
		elif button[0] == 'f': #Function key
			b = button[1:]
			if b=='L0':
				self.display.L0.pressed()
			elif b=='L1':
				self.display.L1.pressed()
			elif b=='L2':
				self.display.L2.pressed()
			elif b=='L3':
				self.display.L3.pressed()
			elif b=='L4':
				self.display.L4.pressed()
			elif b=='L5':
				self.display.L5.pressed()
			elif b=='R0':
				self.display.R0.pressed()
			elif b=='R1':
				self.display.R1.pressed()
			elif b=='R2':
				self.display.R2.pressed()
			elif b=='R3':
				self.display.R3.pressed()
			elif b=='R4':
				self.display.R4.pressed()
			elif b=='R5':
				self.display.R5.pressed()
		else:
			self.page.button_pressed(button)
			
		self.page.load_data()	
class ACT_FPLN(object):
	
	def __init__(self, display, aircraft,data):
		self.display = display
		self.aircraft = aircraft
		self.data = data
		
		self.page_num = 1
		self.page_end = 1
		self.flpn = self.data.flpn
		
	def button_pressed(self, button):
		if button == "EXEC":
			self.execute()
		elif button == "NEXT":
			self.page_down()
		elif button == "PREV":
			self.page_up()
	
	
	def selected(self):
		#This is only called when FLPN button is selected
		self.page_num = self.data.legs_maxpage()
		#self.page_num = 1
		self.display_screen()
		
	def display_screen(self): #This page is selected, set up page.
		self.display.clear_display()
		
		#Header
		self.display.header.add_text( 5 , 'FPLN', "C")
		
		#1st Line
		if self.page_num ==1:
			self.display.L0.set_func(self.set_orgin)
			self.display.R0.set_func(self.set_dest)
			self.display.R1.set_func(self.set_altn)
			self.display.R4.set_func(self.set_fltnum)
			self.display.R3.set_func(self.fix_button)
			self.display.upper[0].add_text(1, 'ORIGIN' , "c")
			self.display.upper[0].add_text(10, 'DIST' , "c")
			self.display.upper[0].add_text(19, 'DEST' , "c")
			#2nd Line
			self.display.upper[1].add_text(1, 'ROUTE' , "c")
			self.display.upper[1].add_text(19, 'ALTN' , "c")
			#3rd Line
			self.display.upper[2].add_text(15, 'ORIG RWY' , "c")
			#4th Line
			self.display.upper[3].add_text(1, 'VIA' , "c")
			self.display.upper[3].add_text_rjust(22, 'TO' , "c")
			#5th Line
			self.display.upper[4].add_text(0, '----------------' , "c")
			self.display.upper[4].add_text_rjust(22, 'FLT NO' , "c")
		else: #Page 2 and up
			self.display.R0.set_func(self.fix_button)
			self.display.R1.set_func(self.fix_button)
			self.display.R2.set_func(self.fix_button)
			self.display.R3.set_func(self.fix_button)
			self.display.R4.set_func(self.fix_button)
			self.display.upper[0].add_text(1, 'VIA' , "c")
			self.display.upper[0].add_text_rjust(22, 'TO' , "c")
		#6th Line
		self.display.main[5].add_text(0, '<SEC FPLN', "W")
		self.display.main[5].add_text_rjust(23, 'PERF INIT>', "W")
		
		
		self.load_data()
		
	def display_data(self):
		#Common to all pages Header
		self.display.header.clear_text()
		self.display.header.add_text( 1 , self.flpn.text, self.flpn.color_size)
		self.display.header.add_text( 10 , self.data.flight_num, "C")
		self.display.header.add_text( 5 , 'FPLN', "C")
		self.display.header.add_text_rjust( 22 , "%d/%d" %(self.page_num, self.page_end), "C")
		#Page 1 Only
		if self.page_num == 1:
			
			if self.flpn.route.dist == None:
				self.display.main[0].add_text(10, '    ' , "w")
			else:
				self.display.main[0].add_text(10, '%4d' %self.flpn.route.dist, "w")
			#Flight num
			self.display.main[4].add_text_rjust(22, self.display.R4.value, "W")
			
				
		self.display.main[0].add_text(1, self.display.L0.value, "W")
		self.display.main[0].add_text_rjust(22, self.display.R0.value, "W")
		self.display.main[1].add_text_rjust(22, self.display.R1.value, "W")
		if self.page_num > 1: 
			self.display.main[2].add_text_rjust(22, self.display.R2.value, "W")
		
		self.display.main[3].add_text_rjust(22, self.display.R3.value, "W", 5)
		self.display.main[4].clear_text()
		
		if self.flpn.text == "MOD":
			self.display.main[4].add_text(0, '<CANCEL MOD' , "W")
			self.display.L4.set_func(self.cancel_mod, True)
		else:
			self.display.main[4].remove_text(0,13)
			self.display.L4.set_func(None, True)
		
		#DEBUGGING
		print "ACTIVE"
		self.data.active_FLPN.route.print_legs()
		print "MOD"
		self.data.mod_FLPN.route.print_legs()
	def load_data(self):
		
		def nav_text(nav, length, empty_char = ' '):
			if nav == None:
				value = empty_char * length
			else:
				value = nav.ID
			return value
		
		
		self.flpn = self.data.flpn
		#Calculate number of pages needed to show all of flight plan
		self.page_end = self.data.legs_maxpage()
		#self.page_end = self.flpn.route.legs.max_page
		
		if self.page_num == 1:
			#Orgin
			self.display.L0.value = nav_text(self.flpn.route.orgin, 4, self.display.empty_box)
			self.display.R0.value = nav_text(self.flpn.route.dest, 4, self.display.empty_box)
			self.display.R1.value = nav_text(self.flpn.alt_route.dest, 5, '-')
					
			#Header	
			#Flight num
			self.display.R4.value = self.data.flight_num
			#Via
			#print self.flpn.route.legs
			
			self.display.R3.value = nav_text(self.flpn.route.get_fix(0), 5, '-')
			
		else: #Page 2 and up
			start_id = (self.page_num - 2) * 5 + 1
			self.display.R0.value = nav_text(self.flpn.route.get_fix(start_id), 5, '-')
			self.display.R1.value = nav_text(self.flpn.route.get_fix(start_id + 1), 5, '-')
			self.display.R2.value = nav_text(self.flpn.route.get_fix(start_id + 2), 5, '-')
			self.display.R3.value = nav_text(self.flpn.route.get_fix(start_id + 3), 5, '-')
		
			
		#Now update data on screen	
		self.display_data()	
				
		
	def execute(self):
		self.data.execute()
		self.load_data()
			
	def page_down(self):
		self.page_num +=1
		if self.page_num > self.page_end:
			self.page_num = self.page_end
		self.display_screen()
	
	def page_up(self):
		print "page_up"
		self.page_num -=1
		if self.page_num < 1:
			self.page_num = 1
		self.display_screen()
		
	def cancel_mod(self, value, button):
		self.data.cancel_mod()
		self.load_data()
		self.selected()
		print "CANCELED MOD"
		
	def set_mod_flpn(self):
		
		self.data.set_mod_flpn()
		self.load_data()
		
	def load_airport(self, s, fix, set_func):
		if s=='@': #Delete
			if fix != None:
				self.set_mod_flpn()
				set_func(None)
			self.display.scratchpad.clear_all()
		elif len(s) != 4:
			self.display.scratchpad.invalid_entry()
		else:
			r = navdata.search(s,navdata.APT.array)
			if len(r) == 1:
				self.set_mod_flpn()
				set_func(r[0])
				self.display.scratchpad.clear_all()
				#self.flpn.route.change_orgin()
				self.load_data()

			elif len(r) == 0:
				self.display.scratchpad.set(" NOT FOUND IN DATABASE", True)
	
	def set_orgin(self, s, button):
		self.load_airport(s, self.flpn.route.orgin, self.data.set_orgin)
		
	def set_dest(self, s ,button):
		self.load_airport(s, self.flpn.route.dest, self.data.set_dest)
		
	def set_altn(self, s , button):
		self.load_airport(s, self.flpn.alt_route.dest, self.data.set_altn)

	def set_fltnum(self, s, button):
		self.display.scratchpad.clear_all()
		if s=='@': #Delete
			self.data.flight_num = ''
		else:
			self.data.flight_num = s[:8] #Cap it at 8
	
	def fix_button(self, s, button):
		#First get the fix index, for this button/
		self.display.scratchpad.clear_all()
		fix = button.value
		if self.page_num == 1: #The only set fix button on page 1 is for fix 0
				id = 0 
		else: #If not page 1 claculate the id
			b = int(button.name[1]) #Covertes button name to interger i.e. R1 to 1
			id = (self.page_num -2) * 5 + 1 + b
			
		#Now determine delete or add etc.
		if s=='@': #Delete
			print button.isblank()
			if not (button.isblank()):
				print "DELETE FIX" , id
				self.delete_fix(id)
		else:
			print "SETTING FIX", s, id
			self.set_fix(s, id) #Set fix to scratchpad value
			
	def set_fix(self, s, id):
			new_legs = self.flpn.route.change_fix(s, id)
			if new_legs != None:
				self.set_mod_flpn()
				self.data.set_legs(new_legs)
				self.selected()
			else:
				self.display.scratchpad.invalid_entry()
				
	def delete_fix(self, id):
			
			new_legs = self.flpn.route.delete_fix(id)
			if new_legs != None:
				self.set_mod_flpn()
				self.data.set_legs(new_legs)
	
