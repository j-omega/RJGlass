#config.py 
# Config file for PyGlass
#
#This imported by PyGlass via  import config
#
#CONSTANTS
TEST = 1 #run test routine (will not recieve any data from Flight Sim program)
FSX = 2 #Recieve data from test routine


# Screen / Window Setup
#X resolution of window
window_x = 1024
#Y resolution of window
window_y = 768
#Full screen
full_screen=False
#Set Mode of program
# TEST = run test routine (will not recieve any data from Flight Sim program)
# FSX = Recieve data from test routine
mode = FSX #Note: case sensitive
#Set Port Number to listen for data on
port = 30000
#Data directory name (The name of the folder where navdata is stored)
data_directory = "data"
#Set max and min lat long values for nav data
#Only points within these ranges will be stored in the Nav Database
max_long= -42
min_long = -180
max_lat = 72
min_lat = 10
