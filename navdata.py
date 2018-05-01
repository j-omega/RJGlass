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
import math

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
		
		

class fix_c(object):
	def __init__(self, type):
		self.array = []
		self.visible = [] # Array of list indexes of objects that are within range and need to be drawn on Moving map
		self.type = type
		self.on = True #If true will be displayed on moving map
	def add(self, list):
		self.array.append(list)
	def cycle_on(self):
		#Used from a keyboard_command to turn on and off different fix types on Moving Map
		if self.on:
			self.on=False
		else:
			self.on=True
	
class flightplan_obj(object):
	#This the class of a flightplan object
	def __init__(self):
		self.num =0 #Number of fixes in plan
		self.points =[] #Array of the fixes
	def add(self, fix):
		self.points.append(fix)
		self.num = len(self.points)
		
class navaid_obj(object):
	def __init__(self, type, ID, lat, long, freq, type2 = "None"):
		#Convert lat long into string
		self.ID = ID
		self.latlong = (math.radians(lat), math.radians(long))
		self.type = type
		self.dist_away =0.0
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
			t.append((c,i))
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
	while apt_file.file_end ==False:
		line_list = apt_file.read()
		
		if line_list[0] == "1":
			ID = line_list[4] #stays as String Airport Name
			#print ID
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
		
	apt_file.close()

#=====================================
#Begin Module Code
FIX = fix_c(FIX_type) #Array of Intersections (5 characters)
VORH = fix_c(VORH_type)#Array of VORH's High altitude VOR's
VORL = fix_c(VORL_type)
NDB = fix_c(NDB_type)#Array of NDB's
APT = fix_c(APT_type) #Array of Airports
APT.on = False
FIX.on = False
flightplan = flightplan_obj()
#nav_list = nav_file(data_dir, 'nav.dat')
load_nav_file(VORH, VORL, NDB)
load_fix_file(FIX)
load_apt_file(APT)
#start = time.time()
#for i in range(1000):
#	d = search("LAX", nav_list)
# Need to make a flight plan
flightplan.add(APT.array[1479])
#flightplan.add(FIX.array[25608])
flightplan.add(VORL.array[186])
flightplan.add(VORH.array[525])
flightplan.add(FIX.array[6426])
#flightplan.add(FIX.array[25614])
flightplan.add(APT.array[316])
if __name__ == "__main__":
	
	def text_search(s, array, name):
		t = search(s.upper(), array)
		if len(t) > 0:
			print name
			for i in t:
				print i[0], i[1].ID, i[1].latlong
#print VOR_fix.array
#	t =  search("LAX",VOR.array)
	
#	print len(VORH.array)
	s="ds"
	while s <> '':
		s = raw_input("Enter Fix / Apt ID :")
		#Search s
		text_search(s, NDB.array, 'NDB')
		text_search(s, APT.array, 'Airports')
		text_search(s, FIX.array, 'Intersections / Fixes')
		text_search(s, VORH.array, 'VOR High Altitude')
		text_search(s, VORL.array, 'VOR Low Altitude')
#	t =  search("AZ", NDB.array)
#	for i in t:
#		print i.ID
#	print "JXN"
#	t = search("KADG", APT.array)
#	for i in t:
#		print i
#	print APT.array[1479].ID
#	print len(APT.array)
	#for i in APT.array:
	#	print i.ID
#print time.time()- start
#print d
