#config.py 
# Config file for PyGlass
#
#This imported by PyGlass via  import config
#
#CONSTANTS
TEST = 1 #run test routine (will not recieve any data from Flight Sim program)
FSXSP0 = 2 #Recieve data from test routine
FSXSP1 = 3
FSXSP2 = 4


# Screen / Window Setup
#X resolution of window
window_x = 1024
#Y resolution of window
window_y = 768
#Full screen
full_screen=False
#Set Mode of program
# TEST = run test routine (will not recieve any data from Flight Sim program)
# FSXSP0 or FSXSP1 or FSXSP2 = Recieve data from FSX Using PySimConnect.py
#mode = TEST #Note: case sensitive
mode = FSXSP0
#FSX Sim Connect (Config) See README on how to configure SimConnect.xml file.
addr = '192.168.1.34'  #IP Address of computer running FSX.
port = 1500
timeout = 25.0  #Number of seconds before Connection to FSX will timeout
#Data directory name (The name of the folder where navdata is stored)
data_directory = "data"
#Set max and min lat long values for nav data
#Only points within these ranges will be stored in the Nav Database
max_long= -42
min_long = -180
max_lat = 72
min_lat = 10
#Ranges for moving map
max_VOR_range = 160.0
max_NDB_range = 80.0
max_APT_range = 160.0
max_FIX_range = 20.0
min_RWY_length = 4500 #The minimum RWY length to be in airport database.
#Speed limits  6 flap postitions on RJ (0, 1, 8, 20, 30, 45)
VNE_flaps = ( 315, 230, 230, 230, 185, 170) 
VS_flaps = (111, 107, 103, 101, 100, 97)
Gear_speed_limit = 220


