#!/usr/bin/env python
# ----------------------------------------------------------
# keyboard MODULE for GlassCockpit procject RJGlass
# ----------------------------------------------------------
# This module will take the keys that are pressed on the keyboard and take appropriate action.
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


from pygame.locals import *

def test():
	print "TEST !@# !@#"

def pressed(key, mods):
	#
	if (mods & KMOD_CTRL):
		k_list = key_list_ctrl
	elif (mods & KMOD_ALT):
		k_list = key_list_alt
	else:
		k_list = key_list
	for i in k_list:
		if i[0] == key:
			i[1]() #Call the function 
		
#Set up association with keys and function upon a keydown event	
#
def setup_lists(aircraft):
	global key_list, key_list_ctrl, key_list_alt
	key_list = [[K_b, aircraft.ND.range.down], [K_v, aircraft.ND.range.up]]
	key_list_ctrl = [[K_v, aircraft.ND.range.down], [K_b, aircraft.ND.range.up]]
	key_list_alt = [[K_v, aircraft.ND.range.down], [K_b, aircraft.ND.range.up]]
	print key_list
