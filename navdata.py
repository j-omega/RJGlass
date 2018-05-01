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
import config
import time


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
		self.filepath = 	os.path.join(dir, filename)
		
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
		
		#Start reading of next line
		t=self.f_obj.readline()
		l = t.split()
		self.count+=1
		#check for file end
		if l[0]=="99": self.file_end = True
		
		return l
		
		

class fix_c(object):
	def __init__(self):
		self.array = []
		
		
	def add(self, list):
		self.array.append(list)
		


def search(fixname, array):
	c=0
	t=[]
	for i in array:
		c+=1
		if i[0]==fixname:
			#print c,i
			t.append(i)
		
	return t

def load_nav_file(VOR, NDB):
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
			if (nav_file.valid(lat, long)): #Make sure it is in lat long limits
				#If Valid then add to appropriate array for memory storage
				if type == 3 : #VOR type
					VOR.add([ID, lat, long, freq/100.0])
				elif type == 2: #NDB type
					NDB.add([ID, lat, long, freq])
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
				FIX.add([ID, lat, long])
	#Error check here later
	#nav_array = data_file.read(f)
	
#	print nav_array
	fix_file.close()

#=====================================
#Begin Module Code
FIX = fix_c() #Array of Intersections (5 characters)
VOR = fix_c()#Array of VOR's
NDB = fix_c()#Array of NDB's

#nav_list = nav_file(data_dir, 'nav.dat')
load_nav_file(VOR, NDB)
load_fix_file(FIX)
#start = time.time()
#for i in range(1000):
#	d = search("LAX", nav_list)

#print VOR_fix.array
print search("LAX",VOR.array)
print len(VOR.array)
print search("AZ", NDB.array)
print len(NDB.array)
print search("DIRTY", FIX.array)
print len(FIX.array)
#print time.time()- start
#print d
