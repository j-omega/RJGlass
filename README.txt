RJGlass v 0.2  README Notes  8/1/07 Michael LaBrie monkey256@verizon.net

Note: This is alpha software. With basic functionality.

This program has been tested to work with FSX (without SP1 installed) using the SimConnect API provided by Microsoft.
This program has been tested to run on Windows XP SP2, as well as Ubuntu Linux (7.04), and with FSX deluxe version.
There are two separate programs that are needed. 
The first one is (RJGlass) a Python OpenGL program that actually renders the CRJ gauges. 
The second is (SimFSX) a C# .NET program that communicates with FSX via the SimConnect API, 
the SimFSX program also communicates via UDP protocol to RJGlass the appropriate aircraft data.

SimFSX has to run on the same computer that FSX is running, and therefore only runs on Windows. 
RJGlass since it is written in Python can run on different flavors of Windows, Linux, or Mac (not tested.)

RJGlass requires a computer with OpenGL support (3D Acceleration)
I currently run RJGlass on a Athalon XP 1400 with a ATI Radeon 9800 Pro, (the computer does not run FSX) and get approximately 100 frames per second. 
As RJGlass progresses and more features are added, the frames per second, will drop.

If you have any questions concerning this program, installing it, or running it. Feel free to contact me at monkey256@verizon.net

Instructions for setup
===============================
Downloading RJGlass

Windows ----

Currently you can download a zip file containing the Windows executable with source, or a zip file with just the source code.
The windows executable version, should be able to run on any Windows machine. No other added software is required to download.
If you want to run straight from the source code and not use the executable on Windows, you need to install Python (version 2.4 or higher), PyOpenGL, GLUT and PyGame.

To run either double click on the RJGlass exe, or if running from the source code double click on the RJGlass.py file.

Linux ----

To install on Linux, RJGlass.py needs to be run with python. In order to run on Linux you must have 3D acceleration working with your video card. 
You also need to install Python (most Linux distro's come with Python already installed) PyOpenGL, GLUT, and PyGame.
If you use Ubuntu you can apt-get install python-OpenGL python-PyGame (This should get everything you need.)

To run either click to run RJGlass.py or from command line do python RJGlass.py

===================================================================================
Config File (config.py)
===================================================================================
To change the configuration settings for RJGlass, you need to edit the config.py file.
Note the config.py file is the only python file, if you go the Windows executable route.
If you download the source, then the config.py file is along with the other .py (python) files.

The file has comments to help, the following are the most frequent changes you will make to it.
The config file is set by default for non fullscreen (windowed mode) 1024x768, and looking for data from SimFSX on port 30000.
===============
The x,y resolution of RJGlass is set by window_x and window_y respectively. (Note: The program is designed for and runs best at 1024x768)
fullscreen=True will give a fullscreen view. fullscreen=False will make it a window within your desktop.

There are two mode's of operation (mode=FSX) (default) will look for UDP data from the SimFSX program. (mode=TEST), will not listen for any data and just render the gauges.

port=30000, sets the port that RJGlass will listen to, for UDP data that is sent to it. (This needs to match the port that SimFSX is sending data too.)

====================================
Downloading SimFSX
(Note: You need to have .NET version 2.0 at least installed on your computer for this to run. I have only tested SimFSX with the deluxe version of FSX)

Download the zip and uncompress it, then run SimFSX executable to run it. (SimFSX has to run on the same computer that FSX is running on.)
Input the IP Address that you want to send the UDP data to. (You can use 127.0.0.1, if RJGlass is running on the same computer as FSX is.)
Input the port that you want the UDP data sent to. (Default is 30000)

Then hit connect to FSX button, and you should see numbers separated by commas in the text box.


===================================
Operation
===================================
To quit out of RJGlass, press the ESC key.
No other keys, or mouse clicks will do anything.