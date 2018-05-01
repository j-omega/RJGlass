RJGlass v 0.3.0  README Notes  2/28/08 Michael LaBrie monkey256@verizon.net

Note: This is beta software. With alot of future functionality in the works.

RJGlass is an open source, OpenGL model of a Canadian Regional Jet (CRJ) Glass Cockpit. It uses the Simconnect API, to recieve data from FSX. It is designed to run on a seperate computer, for a home cockpit type setup.

=========== Major Changes since 0.2 ====================

SimFSX, the C# program that bridges FSX and RJGlass, is no longer needed. 
RJGlass now directly connects to FSX via the SimConnect API.
*****************************************
== NOTE: Since it now connectes directly to FSX, additional steps need to be taken to setup communication link.
== NOTE: In the config.py file, you need to specify which version of FSX you have, either FSXSP0, FSXSP1, or FSXSP2. See config.py section for more details below. 
*****************************************
There is now a need to set up SimConnect on the machine running FSX, using an xml file.
I have included a sample xml file that should work, it allows global connections and sets the listening port to 1500. You can edit this file using a text editor. This file must be located in the correct location.

This file needs to be located in:
For Windows XP: C:\Documents and Settings\Application Data\Microsoft\FSX
For Vista: C:\Users\AppData\Roaming\Microsoft\FSX  (Note: I don't have Vista, to test this.)

If there is already a SimConnect.xml file in this folder, then some other software that uses SimConnect, might have already created that file. If there isn't one in there, then copy the xml file that came with RJGlass in that location.
For RJGlass to connect, there has to be a SimConnect.xml file in that folder and it needs to have a global connection setup and a port specified. The port specfied needs to agree with the port specified in config.py, and the RJGlass folder.

Note: Make sure there is no firewalls setup, that will prohibit RJGlass connecting to the FSX computer on the port selected.

Be sure to setup config.py file with IP address of the FSX machine.

Feel free to contact me if you have questions: monkey256@verizon.net

Here are some links, to explain it a little more what is going on:
http://www.fsdeveloper.com/wiki/index.php?title=Remote_connection
http://forums.avsim.net/dcboard.php?az=show_topic&forum=171&topic_id=38654&mesg_id=38693


*****************************************
More new stuff for 0.3.0
*****************************************
The PFD (Primary Flight Display) is very close to complete. The Flight Mode Annuciator and FMS is not implemented yet, but everything else should be modeled.
New iteams include:
HSI now has working ADF's and VOR's bearing working. Speed Cue's are now modeled on the speed tape.
VSpeed's are now changeable via keyboard inputs. 
The ND (Navigational Display) has primitive moving map. The only area that is working, is near airports KDTW and KADG. All navaids can be cycled on and off on the moving map.
Keyboard now controls PFD.
Other Bug Fixes.

This program has been tested to work with FSX SP0, SP1, & SP2 using the SimConnect API provided by Microsoft.
This program has been tested to run on Windows XP SP2, as well as Ubuntu Linux (7.10), Debian Etch.

RJGlass since it is written in Python can run on different flavors of Windows, Linux, or Mac (not tested.)

RJGlass requires a computer with OpenGL support (3D Acceleration)
I currently run RJGlass on a Athalon XP 3200 with a ATI Radeon 9800 Pro, (the computer does not run FSX) and get approximately 120 frames per second. 

If you have any questions concerning this program, installing it, or running it. Feel free to contact me at monkey256@verizon.net

Instructions for setup
===============================
Downloading RJGlass


Windows ----

Currently you can download a zip file containing the Windows executable and supporting files, or a zip file with just the source code.
The windows executable version, should be able to run on any Windows machine. No other added software is required to download.
If you want to run straight from the source code and not use the executable on Windows, you need to install Python (version 2.4 or higher), PyOpenGL 2.X, GLUT and PyGame.

To run either double click on the RJGlass exe, or if running from the source code double click on the RJGlass.py file.

Linux ----

To install on Linux, RJGlass.py needs to be run with python. In order to run on Linux you must have 3D acceleration working with your video card. 
You also need to install Python (most Linux distro's come with Python already installed) PyOpenGL 2.X, GLUT, and PyGame.
(Note: PyOpenGL 3.X is buggy, and kills the frame rate. Uses PyOpenGL 2.X for best resutsl.)
If you use Ubuntu you can apt-get install python-OpenGL python-PyGame (This should get everything you need.)

To run either click to run RJGlass.py or from command line do: python RJGlass.py

===================================================================================
Config File (config.py)
===================================================================================
To change the configuration settings for RJGlass, you need to edit the config.py file.
Note the config.py file is the only python file, if you go the Windows executable route.
If you download the source, then the config.py file is along with the other .py (python) files.

The file has comments to help, the following are the most frequent changes you will make to it.
The config file is set by default for non fullscreen (windowed mode) 1024x768, and trys to connect to FSX on port 1500.
===============
The x,y resolution of RJGlass is set by window_x and window_y respectively. (Note: The program is designed for and runs best at 1024x768)
fullscreen=True will give a fullscreen view. fullscreen=False will make it a window within your desktop.

There are multiple mode's of operation (mode=FSXSP0 or FSXSP1 or FSXSP2 (default)) will attempt to connect to FSX. (mode=TEST), will not listen for any data and just render the gauges. You must specifiy the correct version of FSX, either SP0, SP1, or SP2.

port=1500, sets the port that RJGlass will try to connect to SimConnect on. 
**** VERY IMPORTANT: You need to put a special XML file in the coorect spot on the computer running FSX, so to allow RJGlass to connect. Also, you may have to open up port 1500, in firewalls (Windows / router ) 

===================================
Operation
===================================
To quit out of RJGlass, press the ESC key or Ctrl-Q.
Mouse doesn't do anything on RJGlass, keyboard assignments are below.

KEYBOARD ASSIGNMENTS

	ND
PgDn	------	Decrease Moving Map range
PgUp	------	Increase Moving Map range
n	------	Cycle NDB's on and off
v	------ 	Cycle VOR's on and off
a	------	Cycle APT's on and off
f	------	Cycle Fixes (Intersections) on and off

	HSI
1	------	Cycle HSI's Bearing 1
2	------	Cycle HSI's Bearing 2
TAB	------	Change Nav Source (Nav1 or Nav2)

	VSpeeds
Alt-z	------	Cycle thru Vspeed selected (V1/VR/V2/VT)
Ctrl-z	------	Vspeed Visible (On/Off)
z	------	Increase selected Vspeed
Shift-z	------ 	Decrease selected Vspeed

	Decision Height (DH)
Ctrl-d	------	DH Visible (On/Off)
d	------	Increase DH
Shift-d	------ 	Decrease DH

	MDA (Decision Altitude)
Ctrl-m	------	MDA Visible (On/Off)
m	------	Increase MDA
Shift-m ------	Decrease MDA

========= END ==================
