#!/usr/bin/env python
# ----------------------------------------------------------
# FMS_button MODULE for GlassCockpit procject RJGlass
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

class button(object):

    def __init__(self, name, x1,y1,x2,y2):
        self.name = name
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        
    
    def check(self, (x, y)):
    #Checks to see if x,y coordinates within button boundries
        if ((self.x1 < x < self.x2) & (self.y1 < y < self.y2)):
            return True
        else: 
            return False

class button_list_c(object):

   
    def add(self, name , (x1,x2),(y1,y2)):
        self.list.append(button(name, x1,y1,x2,y2))
    
    def __init__(self):
        self.list = []
        #Function Keys
        x_func_left = (42,77)
        x_func_right = (439,474)
        y_func = [(i*39+115,i*39+115+27) for i in range(6)]
        #Add the buttons (name, (x1,x2) , (y1,y2)
        #FUNCTIONS KEYS
        self.add('fL0', x_func_left, y_func[0])  
        self.add('fL1', x_func_left, y_func[1])  
        self.add('fL2', x_func_left, y_func[2])  
        self.add('fL3', x_func_left, y_func[3])  
        self.add('fL4', x_func_left, y_func[4])  
        self.add('fL5', x_func_left, y_func[5])  
        self.add('fR0', x_func_right, y_func[0])  
        self.add('fR1', x_func_right, y_func[1])  
        self.add('fR2', x_func_right, y_func[2])  
        self.add('fR3', x_func_right, y_func[3])  
        self.add('fR4', x_func_right, y_func[4])  
        self.add('fR5', x_func_right, y_func[5])  
        #Page buttons
        x_page = [(i*60+22, i*60+71) for i in range(8)]
        y_page = [(i*44+415, i*44+451) for i in range(4)]
        #First Row
        self.add('MSG', x_page[0], y_page[0])
        self.add('DIR', x_page[1], y_page[0])
        self.add('FPLN', x_page[2], y_page[0])
        self.add('DPAR', x_page[3], y_page[0])
        self.add('HOLD', x_page[4], y_page[0])
        self.add('UP', x_page[5], y_page[0])
        self.add('PREV', x_page[6], y_page[0])
        self.add('NEXT', x_page[7], y_page[0])
        #Second Row
        self.add('INDEX', x_page[0], y_page[1])
        self.add('FIX', x_page[1], y_page[1])
        self.add('LEGS', x_page[2], y_page[1])
        self.add('SFPLN', x_page[3], y_page[1])
        self.add('VNAV', x_page[4], y_page[1])
        self.add('DOWN', x_page[5], y_page[1])
        self.add('MCDU', x_page[6], y_page[1])
        self.add('EXEC', x_page[7], y_page[1])
        #Third Row
        self.add('RADIO', x_page[0], y_page[2])
        self.add('PROG', x_page[1], y_page[2])
        self.add('PERF', x_page[2], y_page[2])
        #Fourth Row
        self.add('MFDD', x_page[0], y_page[3])
        self.add('MFDM', x_page[1], y_page[3])
        self.add('MFDA', x_page[2], y_page[3])
        #Alpha Keys
        x_alpha = [(i*47+225, i*47+258) for i in range(5)]
        y_alpha = [(i*43+510, i*43+543) for i in range(6)]
        #1st Row
        self.add('A', x_alpha[0], y_alpha[0])
        self.add('B', x_alpha[1], y_alpha[0])
        self.add('C', x_alpha[2], y_alpha[0])
        self.add('D', x_alpha[3], y_alpha[0])
        self.add('E', x_alpha[4], y_alpha[0])
        #2nd Row
        self.add('F', x_alpha[0], y_alpha[1])
        self.add('G', x_alpha[1], y_alpha[1])
        self.add('H', x_alpha[2], y_alpha[1])
        self.add('I', x_alpha[3], y_alpha[1])
        self.add('J', x_alpha[4], y_alpha[1])
        #3rd Row
        self.add('K', x_alpha[0], y_alpha[2])
        self.add('L', x_alpha[1], y_alpha[2])
        self.add('M', x_alpha[2], y_alpha[2])
        self.add('N', x_alpha[3], y_alpha[2])
        self.add('O', x_alpha[4], y_alpha[2])
        #4th Row
        self.add('P', x_alpha[0], y_alpha[3])
        self.add('Q', x_alpha[1], y_alpha[3])
        self.add('R', x_alpha[2], y_alpha[3])
        self.add('S', x_alpha[3], y_alpha[3])
        self.add('T', x_alpha[4], y_alpha[3])
        #5th Row
        self.add('U', x_alpha[0], y_alpha[4])
        self.add('V', x_alpha[1], y_alpha[4])
        self.add('W', x_alpha[2], y_alpha[4])
        self.add('X', x_alpha[3], y_alpha[4])
        self.add('Y', x_alpha[4], y_alpha[4])
        #6th Row
        self.add('Z', x_alpha[0], y_alpha[5])
        self.add(' ', x_alpha[1], y_alpha[5])
        self.add('DEL', x_alpha[2], y_alpha[5])
        self.add('/', x_alpha[3], y_alpha[5])
        self.add('CLR', x_alpha[4], y_alpha[5])
        #Numbers
        x_num = [(i*47+66, i*47+103) for i in range(3)]
        y_num = [(i*43+595, i*43+630) for i in range(4)]
        #1st Row
        self.add('1', x_num[0], y_num[0])
        self.add('2', x_num[1], y_num[0])
        self.add('3', x_num[2], y_num[0])
        #2nd Row
        self.add('4', x_num[0], y_num[1])
        self.add('5', x_num[1], y_num[1])
        self.add('6', x_num[2], y_num[1])
        #3rd Row
        self.add('7', x_num[0], y_num[2])
        self.add('8', x_num[1], y_num[2])
        self.add('9', x_num[2], y_num[2])
        #4th Row
        self.add('.', x_num[0], y_num[3])
        self.add('0', x_num[1], y_num[3])
        self.add('+-', x_num[2], y_num[3])
 
