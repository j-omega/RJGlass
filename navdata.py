#navdata.py  Module to read and store all navigational data, fixes, VOR's, NDB etc, for use by moving map and FMS
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
#import config
import time
import copy
import math
import formula

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


VORH_type = 1
VORL_type = 2
NDB_type = 3
FIX_type = 4
APT_type = 5


class data_file_c(object):
	
	
	def __init__(self, filename):
		#Get from config file the ranges for the filtering of nav data
		self.max_lat = config.max_lat
		self.min_lat = config.min_lat
		self.max_long = config.max_long
		self.min_long = config.min_long
		#Determine path for file
		cwd = os.getcwd()
		dir = os.path.join(cwd, config.data_directory)
		self.filepath = os.path.join(dir, filename)
		
	def open(self):
		self.f_obj = open(self.filepath)
		self.count =0
		self.file_end=False
		
	def close(self):
		self.f_obj.close()
		
	def valid(self,lat,long):
		if (self.max_lat > lat > self.min_lat) & (self.max_long > long > self.min_long):
			return True
		else:
			return False
			
	
	def decode(self,line):
		
		l = line.split() #Takes out all white space return list
		#Check for end 
		#print l
		if len(l) >0:
			if l[0] == "99":
				list = -1
				print "FILE _ENDED"
			else:
				lat = float(l[1])
				long = float(l[2])
				freq = l[4]
				ID = l[7]
				type=l[0]
			
			#if (self.max_lat > lat > self.min_lat) & (self.max_long > long > self.min_long):
			if 1==1:
				#Check to see if fix in within lat long requirements
				list = [ID,lat,long,freq,type]
			else: list=[]
		return list
	
	def read(self):
		
		
		if self.count ==0:	#Start of read, initialize
		#Skip first three lines
			self.f_obj.readline()
			self.f_obj.readline()
			self.f_obj.readline()
		mike =0
		#Start reading of next line
		while mike ==0:
			t=self.f_obj.readline()
			l = t.split()
			self.count+=1
			mike = len(l)
		#check for file end
		if l[0]=="99": self.file_end = True
		
		return l
		
		
class awy_c(object):
	def __init__(self):
		#self.fixes = [] #Array of an array of fixes.
		#Dictionary of each awarway and its data
		self.dict = {} #List of all airways and their locations
	
	
	def check_fix(self,name, list):
			index = [] #empty list
			l = []
			count = 0
			for i in list:
				if name in i:
					index.append(count)
					l.append(i)
				count +=1	
				
			return index
	
		#returns index of list where name is present
	def check_for_end(self, end, r, list, route):
		startfix = route[-1]
		#print "CHECK FOR END", r, startfix, list, route
		if ((not self.end_done) & (list != [])):
			if len(r)>0:
				for y in r:
					if end in list[y]:
						self.end_done= True
						route.append(end)
						self.end_route = copy.copy(route)
					else:
						#Adds next waypoiny
						if list[y][0] == startfix:
							r3 = route + [list[y][1]]
						else:
							r3 = route + [list[y][0]]
						new = list[:y] + list[y+1:]
						r4 = self.check_fix(r3[-1], new)
						#print "R4", r4, r3[-1], new
						self.check_for_end(end, r4, new, r3)
	
	
	def get_route(self, airway, start, end):
		#This will get the route of a airway. By airway name and start fix and end fix.
		
		result = [] #Set to return None unless route if found
		self.end_done = False
		self.end_route = []
		if self.dict.has_key(airway):
			#See if start point exists
			done = False
			list = self.dict[airway]
			r = self.check_fix(start, list)
			if len(r)>0: #If stuff found
				self.check_for_end(end, r, list, [start])
						
												
				#else: 
			
		else: 
			print "AIRWAY NOT FOUND"
			
		return self.end_route
	
class fix_c(object):
	def __init__(self, type, range):
		self.array = []
		self.visible = [] # Array of list indexes of objects that are within range and need to be drawn on Moving map
		self.type = type
		self.on = True #If true will be displayed on moving map
		self.max_range = range
		
	def add(self, list):
		self.array.append(list)
	def cycle_on(self):
		#Used from a keyboard_command to turn on and off different fix types on Moving Map
		if self.on:
			self.on=False
		else:
			self.on=True
	def find_closest(self):
		#This find the closest non visible fix.
		d = 500000.0
		temp = None
		for fix in self.array:
			if 0< fix.total_travel_away < d:
				temp = fix
				d= fix.total_travel_away
				
		self.closest =  temp
		#print "Closest", temp.ID
		
	def add_to_visible(self, fix):
		
		self.visible.append(fix)
		fix.total_travel_away = -2 #Make negative so it isn't checked
		#print "Added",  fix.ID
		
	def remove_from_visible(self,fix, total_dis_traveled, planelat, planelon):
		self.visible.remove(fix)
		fix.total_travel_away = formula.dist_latlong_nm((fix.latlong),(planelat,planelon)) + total_dis_traveled
		#print "Removed", fix.ID
		
	def check_closest(self, total_dis_traveled, planelat, planelon):
		#See if closest navaid is within limits
		fix = self.closest
		#print "Prelim ", fix.ID, fix.total_travel_away, total_dis_traveled
		if fix.total_travel_away <= (total_dis_traveled + self.max_range): #Recheck
			d = formula.dist_latlong_nm((fix.latlong),(planelat,planelon))
			#print "Checking", fix.ID, d
			if d <= self.max_range:
				self.add_to_visible(fix)
				self.find_closest()
			#Else navaid not in range, reclaclulate distance find new closest to check
			else:
				fix.total_travel_away = total_dis_traveled + d
				self.find_closest() #Look for possible newest closest
			
					
class flightplan_obj(object):
	#This the class of a flightplan object
	def __init__(self):
		self.num =0 #Number of fixes in plan
		self.points =[] #Array of the fixes
	def add(self, fix):
		self.points.append(fix)
		self.num = len(self.points)
		fix.inFlightplan = True
		
class navaid_obj(object):
	def __init__(self, type, ID, lat, long, freq, type2 = "None"):
		#Convert lat long into string
		self.ID = ID
		self.latlong = (math.radians(lat), math.radians(long))
		self.type = type
		self.total_travel_away =0.0
		self.inFlightplan = False
		#VOR TYPE
		if (type == VORH_type) | (type== VORL_type):
			self.Freq = "%5.2F" %freq  #Convert freq into string
			if type2 == "VOR":
				self.TACAN = False
			else:
				self.TACAN = True
		elif type == NDB_type:
			self.Freq = "%3d" % freq
		else:
			self.Freq = None
			
def search(fixname, array):
	c=0
	t=[]
	for i in array:
		if i.ID==fixname:
			#print c,i
			t.append(i)
		c+=1
	return t


def load_nav_file(VORH, VORL, NDB):
	#Set indexes for this file
	nav_file = data_file_c( 'nav.dat')
	nav_file.open()
	while nav_file.file_end ==False:
		line_list = nav_file.read()

		#Check to see if its the last line
		if (line_list[0] <> "99"):#The code for VOR's
			#Decode object
			type = int(line_list[0])			
			ID = line_list[7] #stays as String
			freq = int(line_list[4])
			lat = float(line_list[1])
			long = float(line_list[2])
			type2 = line_list[-1] #Gets last part of line, if VOR that will say either VOR, VORTAC, VOR-DME
			range = int(line_list[5])
			if (nav_file.valid(lat, long)): #Make sure it is in lat long limits
				#If Valid then add to appropriate array for memory storage
				if type == 3 : #VOR type
					if range>=80: #If range is over 80 miles add to VOR high list otherwise VOR low list
						VORH.add(navaid_obj(VORH_type, ID, lat, long, freq/100.0, type2))
					else:
						VORL.add(navaid_obj(VORL_type, ID, lat, long, freq/100.0, type2))
						
				elif  type == 2 : #NDB type
					NDB.add(navaid_obj(NDB_type,ID, lat, long, freq, range))
				
	#Error check here later
	#nav_array = data_file.read(f)
#	print nav_array
	nav_file.close()
	
def load_fix_file(FIX):
	#Set indexes for this file
	fix_file = data_file_c( 'fix.dat')
	fix_file.open()
	while fix_file.file_end ==False:
		line_list = fix_file.read()

		#Check to see if its the last line
		if (line_list[0] <> "99"):#The code for VOR's
			#Decode object
			ID = line_list[2] #stays as String
			lat = float(line_list[0])
			long = float(line_list[1])
			if (fix_file.valid(lat, long)): #Make sure it is in lat long limits
			#If Valid then add to appropriate array for memory storage
			#Check to make sure FIX is 5 characters no number
				ok = True
				for c in ID:
					if c.isdigit():
						ok = False
				if ok:
					FIX.add(navaid_obj(FIX_type, ID, lat, long, 0.0))
	
	fix_file.close()
	
	
def load_apt_file(APT):
	#Set indexes for this file
	apt_file = data_file_c( 'apt.dat')
	apt_file.open()
	#f = file("test.dat","w")
	while apt_file.file_end ==False:
		line_list = apt_file.read()
	
		if line_list[0] == "1":
			ID = line_list[4] #stays as String Airport Name
			name = ""
			for a in line_list[5:]:
				name+=a
				name+=" "
			name = name[:-1]
			
			#Scan through all airport code
			rwy_length = 0
			count =0
			lat, long = 0 , 0
			#Loop
			line_list = apt_file.read() #Read next line
			while (line_list[0] == "10"):
				
				if line_list[3] <> "xxx": #Check to see if runway and not taxiway
					#print line_list
					lat += float(line_list[1])
					long += float(line_list[2])
					count +=1
					#Check if runway is max length
					length = int(line_list[5])
					if length > rwy_length:
						rwy_length = length
				line_list = apt_file.read() #Read next line		
				#Determine average lat long to "center" airport
				
			#print ID
			lat = lat / count
			long = long / count
			if (apt_file.valid(lat, long)) & (rwy_length >= config.min_RWY_length): #Make sure it is in lat long limits
		#If Valid then add to appropriate array for memory storage
		#Check to make sure FIX is 5 characters no number
				APT.add(navaid_obj(APT_type, ID, lat, long, 0.0))
				#f.write("%s,%s,%f,%f\n" %(ID,name,lat,long))
	apt_file.close()
	
def load_awy_file(AWY):
	#Set indexes for this file
	awy_file = data_file_c( 'awy.dat')
	awy_file.open()
	#f = file("test.dat","w")
	#temp_list = []
	AWY.list = []
	line_list = awy_file.read()
	while awy_file.file_end ==False:
		lat = float(line_list[1])
		long = float(line_list[2])
		#Frist do latlong check on all data and put data in memory (temp_list)
		if (awy_file.valid(lat, long)):
			airway = line_list[9]
			for a in airway.split('-'):
				#temp_list.append([a, line_list[0],line_list[3]])
				if a not in AWY.list:
					AWY.list.append(a)
				#Add to dict	
				out = [line_list[0], line_list[3]]
				if AWY.dict.has_key(a): #Check to see if airway already exists
					if out not in AWY.dict[a]: #Check for duplicates
						AWY.dict[a].append(out)
				else: #No airway present, so make new airway
					AWY.dict[a] = [out]
						
		line_list = awy_file.read()
	awy_file.close()
	
def fix_search(name):
	
	result = []
	if len(name) == 3:
		result = search(name, VORH.array) + search(name, VORL.array) + search(name, NDB.array)
	elif len(name) == 5:
		result = search(name, FIX.array)
	elif len(name) == 2:
		result = search(name, NDB.array)
	elif len(name) == 4:
		result = search(name, APT.array)
	
	return result
#=====================================
#Begin Module Code
FIX = fix_c(FIX_type, config.max_FIX_range) #Array of Intersections (5 characters)
VORH = fix_c(VORH_type, config.max_VOR_range)#Array of VORH's High altitude VOR's
VORL = fix_c(VORL_type, config.max_VOR_range)
NDB = fix_c(NDB_type, config.max_NDB_range)#Array of NDB's
APT = fix_c(APT_type, config.max_APT_range) #Array of Airports
AWY = awy_c() #Array of airways with fixes
APT.on = False
FIX.on = False
NDB.on = False
flightplan = flightplan_obj()

print "Loading VOR's and NDB's...."
load_nav_file(VORH, VORL, NDB)

print "Loading Fixs ...."
load_fix_file(FIX)

print "Loading Airports ....."
load_apt_file(APT)

print "Loading Airway ....."
load_awy_file(AWY)

#start = time.time()
#for i in range(1000):
#	d = search("LAX", nav_list)
# Need to make a flight plan
#flightplan.add(APT.array[1479])
#flightplan.add(FIX.array[25608])
#flightplan.add(VORL.array[186])
#flightplan.add(VORH.array[525])
#flightplan.add(FIX.array[6426])
#flightplan.add(FIX.array[25614])
#flightplan.add(APT.array[316])
if __name__ == "__main__":
	
	def text_search(s, array, name):
		t = search(s.upper(), array)
		if len(t) > 0:
			print name
			for i in t:
				print i[0], i[1].ID, i[1].latlong
				
	#print AWY.dict
	print len(AWY.dict)
	#print AWY.fixes	
	print "DONE"
	print AWY.dict['V520']
	#print AWY.get_route('J16', 'BTG', 'FSD')
	#print AWY.get_route('J16', 'FSD', 'BTG')
	#print AWY.get_route('J16', 'BTG', 'BOS')
	#print AWY.get_route('J16', 'BOS', 'BTG')
	print AWY.get_route('V520', 'LKT', 'MQG')
	print AWY.get_route('V520', 'LTJ', 'LKT')
	print AWY.get_route('V545', 'HTN', 'ISN')
	#print AWY.dict['J16']
	#for i in range(100,120,1):
	#	print AWY.list[i]
	#	print AWY.fixes[i]
#print VOR_fix.array
#	t =  search("LAX",VOR.array)
	
#	print len(VORH.array)
#	s="ds"
#	while s <> '':
#		s = raw_input("Enter Fix / Apt ID :")
#		#Search s
#		text_search(s, NDB.array, 'NDB')
#		text_search(s, APT.array, 'Airports')
#		text_search(s, FIX.array, 'Intersections / Fixes')
#		text_search(s, VORH.array, 'VOR High Altitude')
#		text_search(s, VORL.array, 'VOR Low Altitude')
#	t =  search("AZ", NDB.array)
#	for i in t:
#		print i.ID
#	print "JXN"
#	t = search("KADG", APT.array)
#	for i in t:
#		print i
#print APT.array[1479].ID
#	print len(APT.array)
	#for i in APT.array:
	#	print i.ID
#print time.time()- start
#print d

