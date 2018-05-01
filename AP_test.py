#!/usr/bin/env python


import autopilot
from PySimConnect import *
import time
import curses



step  = 0.1
bank = data_obj(0.0)
pitch = data_obj(0.0)
head_bug = data_obj(0)
aileron = data_obj(0)
heading = data_obj(0.0)
elev_trim = data_obj(0.0)
vs = data_obj(0)
aileron_pos = event_obj(0)
elevtrim_pos = event_obj(0)
altimeter = data_obj(0)
IAS = data_obj(0.0)
s = SimConnect('RJGlass', config.FSXSP2, True)
s.connect(config.addr, config.port, True)
#Add definition's
s.definition_0 = s.create_DataDefinition(2)
#Data definition ID 2, is the high priority data, that needs to have no delay.
#s.definition_0.add("Airspeed Indicated", "knots", FLOAT32, self.airspeed.IAS)
s.definition_0.add("Indicated Altitude", "feet", INT32, altimeter)
s.definition_0.add("Attitude Indicator Pitch Degrees", "degrees", FLOAT32, pitch)
s.definition_0.add("Attitude Indicator Bank Degrees", "degrees", FLOAT32, bank)
s.definition_0.add("AUTOPILOT HEADING LOCK DIR","degrees", INT32, head_bug)
s.definition_0.add("HEADING INDICATOR","degrees", FLOAT32, heading)
s.definition_0.add("VERTICAL SPEED","ft/min", INT32, vs)
s.definition_0.add("AIRSPEED INDICATED", "Knots", FLOAT32, IAS)
s.definition_0.add("ELEVATOR TRIM INDICATOR", "", FLOAT32, elev_trim)
s.definition_0.add("AILERON POSITION", "", FLOAT32, aileron)
sevent = SimConnect('RJGlass Event', config.FSXSP2, True)
sevent.connect(config.addr, config.port, False)		
sevent.eventlist = sevent.create_EventList()
sevent.eventlist.add("AILERON_SET", aileron_pos)
sevent.eventlist.add("ELEVATOR_TRIM_SET", elevtrim_pos)

global_time = time.time()
#bank_PID = autopilot.PID_c(0.135, 0.1, 1.0, 0.0, 0.38 *3, 0.08, 0.8, -0.8, global_time)
#Kp, alpha, beta, gamma, Ti, Td, umax umin
#Kp cycle 0.27 original 

#Ti 0.38 continuous cycling
#bank_PID = autopilot.PID2_c((0.45 * 0.5), (2/ 1.5), (0.4 ), (1.0 / 8), 0.8, -0.8, 0.1, 6.0, 1.0, global_time)
#bank_PID = autopilot.PID2_c((0.35 * 0.5), (2/ 1.5), (0.8), (0.005 / 8), 0.8, -0.8, 0.30, 6.0, 0.2, global_time)
#Kp, Ti, Td, u_max, u_min, global_time
bank_PID = autopilot.PID2_c(-16383, global_time, aileron, -16383)
bank_PID.set_gains((0.35* 0.5), (2/1.5), (1.5 /8))
bank_PID.set_I_limit(0.4)
bank_PID.set_u_limit(0.6)
bank_PID.set_Roc_curve(66.0, 0.2, 10000.3)

heading_PID = autopilot.PID2_c(30.0, global_time, bank, 30.0)
heading_PID.set_gains((0.08), (5), (0.00001))
heading_PID.set_I_limit(0.05)
heading_PID.set_u_limit(1.0)

#pitch_PID = autopilot.PID_c(0.030, 0.1, 1.0, 0.0, 0.28 * 3, 0.08, 0.7, -0.7, global_time)
#Kp, alpha, beta, gamma, Ti, Td, umax umin
#Below is pitch_PID for degree
pitch_PID = autopilot.PID2_c(-10000, global_time, elev_trim, 16383)
#(0.08), (2 /1.5), (0.4), (1.5/ 8.0), 0.8, -0.8, 1.2, 1.0, 0.1, global_time)
pitch_PID.set_gains((0.08), (2/1.5), (1.5/8))
pitch_PID.set_I_limit(0.4)
pitch_PID.set_u_limit(0.8)
pitch_PID.set_Roc_curve(1.2, 1.0, 0.1)
#Here is VS one below
#VS_PID = autopilot.PID2_c((0.18*0.6), (5.5/2), (0.4), (5.5/ 8.0), 0.3, -0.3, 0.5, 0.1, 0.005, global_time)
#VS_PID = autopilot.PID2_c(-10000, global_time, elev_trim, 16383)
#VS_PID.set_gains((0.18*0.6), (5.5/2), (5.5/8.0))
#VS_PID.set_I_limit(0.4)
#VS_PID.set_u_limit(0.3)
#VS_PID.set_Roc_curve(0.1, 0.005, 0.5)
#Altitude capture per brother at 3000fpm start capture at 1000 ft out,  500fpm start capture at 50ft
ALT_CAP_PID = autopilot.PID2_c(-1, global_time, None, 0)
ALT_CAP_PID.set_gains(0.003, (200000), (0.0000001)) #Set I and P gains to make controller P only
ALT_CAP_PID.set_u_limit(8.0) #Limit it to 8000 fpm
ALT_CAP_PID.set_I_limit(0.0001)
VS_PID = autopilot.PID3_c(10000, global_time, elev_trim, 16383)
VS_PID.set_gains((0.18* 0.6), (5.5/2), (5.5/8.0))
VS_PID.set_I_limit(0.4)
VS_PID.set_u_limit(0.3)

#Here is IAS Speed Hold
#pitch_PID = autopilot.PID2_c((0.092*0.6), (60/2), (0.4), (60.0/ 8.0), 0.3, -0.3, 0.5, 0.2, 0.005, global_time)
#head_PID = autopilot.PID2_c((1.6/ 20), 100000, 0, 0.0000008, 1.0, -1.0, global_time)
time.sleep(2)
s.receive()
bank_ref = 0.0
#pitch_ref= 2.5 #250 Knot
pitch_ref = 0.0
VS_ref = 0.0
heading_ref = 220.0
AP_pitch = False
AP_bank = False

start_time = time.time()

go = True
stdscr = curses.initscr()
stdscr.nodelay(1)
#Setup links
data = VS_PID
f= open("Log.txt", "w")
while go:
	
	s.definition_0.request(4, DataDefinition.USER, DataDefinition.ONCE, interval = 0, flag = 0)
	time.sleep(1.0 /15)
	s.receive()
	stdscr.addstr(2,10, "Pitch %5.2f Bank %5.2f  VS %6d  HDG %4.1f IAS %4.1f Altimeter %7d  " %(pitch.value, bank.value, vs.value, heading.value, IAS.value, altimeter.value))
	stdscr.addstr(3,10, "Elev Trim %6d Aileron Pos %5.3f  " %((elev_trim.value * 10000),(aileron.value * 16383)))
	
	global_time = time.time()
	#head_PID.calc(heading.value, 180, global_time)
	#bank_ref = head_PID.u * 30.0
	#Need to look at IAS to calculate Kp gain.
	gain = (IAS.value * .02 / 100) + 0.028 #Simple Linear function 0.08 @ 260 knots 0.06 @ 160 knots
	if gain> 0.08: gain = 0.08 #Cap it at 0.08
	heading_PID.Kp = gain
	heading_PID.calc(heading.value, heading_ref, global_time, check180=True)
	bank_ref = heading_PID.out
	bank_PID.calc(bank.value, bank_ref, global_time)
	aileron_pos.value = int(bank_PID.out) #int(-16383 * bank_PID.u)
	pitch_PID.calc(pitch.value, pitch_ref, global_time)
	ALT_CAP_PID.calc(altimeter.value, 13000, global_time)
	VS_ref = ALT_CAP_PID.out
	VS_PID.calc(vs.value/ 1000.0, VS_ref, global_time)
	#elevtrim_pos.value = int(pitch_PID.out)
	elevtrim_pos.value = int(VS_PID.out)
	#pitch_PID.calc(IAS.value / 100.0, pitch_ref, global_time)
	#pitch_ref = abs(altimeter.value - 15000) * 3.5
	#if pitch_ref > 1000:
	#	pitch_ref = 1000
	#elif pitch_ref < 50:
	#	pitch_ref = 50
	#if 15000 < altimeter.value:
	#	pitch_ref = pitch_ref * -1
		
	#pitch_ref = pitch_ref / 1000.0
	#pitch_PID.calc(vs.value / 1000.0, pitch_ref, global_time)
	#elevtrim_pos.value = int(-10000 * pitch_PID.u)
	#if abs(bank_PID.u > 0.95): print "SATURATION"
	if AP_bank:
		stdscr.addstr(4, 10, "Bank U %5.2f Aileron %8d Ref %5.2f  %5.2f   " %(bank_PID.u, aileron_pos.value, bank_PID.Ref, bank_ref), curses.A_REVERSE)
		stdscr.addstr(5, 10, "Head U %5.2f Bank %5.2f Ref %5.2f %5.2f   " %(heading_PID.u, bank.value, heading_PID.Ref, heading_ref), curses.A_REVERSE)
	else:
		stdscr.addstr(4, 10, "Bank U %5.2f Aileron %8d Ref %5.2f %5.2f    " %(bank_PID.u, aileron_pos.value, bank_PID.Ref, bank_ref))
		stdscr.addstr(5, 10, "Head U %5.2f Bank %5.2f Ref %5.2f %5.2f   " %(heading_PID.u, bank.value, heading_PID.Ref, heading_ref))
	if AP_pitch: 
		stdscr.addstr(8, 10, "Pitch U %5.2f ElevTrim %8d Ref %5.2f %5.2f    " %(pitch_PID.u, elevtrim_pos.value, pitch_PID.Ref, pitch_ref), curses.A_REVERSE)
		stdscr.addstr(9, 10, "Pitch U %5.2f VertSpeed %8d Ref %5.2f %5.2f    " %(VS_PID.u, vs.value, VS_PID.Ref, VS_ref), curses.A_REVERSE)
	else:
		stdscr.addstr(8, 10, "Pitch U %5.2f ElevTrim %8d Ref %5.2f %5.2f    " %(pitch_PID.u, elevtrim_pos.value, pitch_PID.Ref, pitch_ref))
		stdscr.addstr(9, 10, "Pitch U %5.2f ElevTrim %8d Ref %5.2f %5.2f    " %(VS_PID.u, elevtrim_pos.value, VS_PID.Ref, VS_ref))
	#aileron_pos.value = 100
	
	stdscr.addstr(11,14, "P= %06.3f I= %06.3f D= %06.3f     " %(data.P * data.Kp, data.I * data.Kp, data.D * data.Kp))
	stdscr.addstr(17,10, "ALT CAP VS %7d" %(ALT_CAP_PID.out * 1000.0))
	#stdscr.addstr(10,14, "P= %06.3f I= %06.3f D= %06.3f Ref = %5.3f    " %(pitch_PID.P * pitch_PID.Kp, pitch_PID.I * pitch_PID.Kp, pitch_PID.D * pitch_PID.Kp, pitch_PID.Ref))
	if AP_bank: sevent.eventlist.list[0].send()
	if AP_pitch: sevent.eventlist.list[1].send()
	
	
	diff = global_time - start_time
	if diff > 40: 
		#f.close()
		#pass
		bank_ref = 0.0
		pitch_ref = 0.0
		#start_time = global_time
		heading_ref = 180
		VS_ref = 0.0
	elif diff > 20: 
		#bank_ref = 30.0
		heading_ref = 225
		pitch_ref = 0.0
		VS_ref = 1.2
	#elif diff > 20: bank_ref = -30.0
	#if diff > 60: 
	#	pitch_ref = 0.0
	#	start_time = global_time
	#elif diff > 40: pitch_ref = 10.0
	#elif diff >40: 
		#pitch_ref = 0.0
		
	#elif diff > 40:
		#pitch_ref = -1.0

	#elif diff > 30:
		
		#pitch_ref = 0.0
	elif diff > 20:
		#pitch_ref = 1.0
		bank_ref = -30.0
		pitch_ref = -0.0
	if diff > 15:
	#f.write("%9.6f , %9.6f , %4.2f, %5.3f, %5.3f, %5.3f\n" %(diff - 15.0, vs.value/1000.0, pitch_PID.Ref, pitch_PID.P * 10 * pitch_PID.Kp, pitch_PID.I * pitch_PID.Kp * 10, pitch_PID.D * 10 * pitch_PID.Kp))
		f.write("%9.6f , %9.6f , %4.2f, %5.3f, %5.3f, %5.3f\n" %(diff - 15.0, vs.value, VS_PID.Ref, VS_PID.P * 10 * VS_PID.Kp, VS_PID.I * VS_PID.Kp * 10, VS_PID.D * 10 * VS_PID.Kp))
	#f.write("%20.8f , %9.6f, %7d\n" %(global_time, VS_PID.Ref, vs.value))
	stdscr.addstr(12,15, "Kp = %5.3f Ti = %5.3f Td = %5.3f ROC = %3.2f Step = %f   " %(data.Kp, data.Ti, data.Td, data.max_Roc, step))
	stdscr.addstr(15,15, "Time = %5.1f" %diff)
	#Check for key press
	c = stdscr.getch()
	if c == 27: go = False
	elif c == ord('p'):
		if AP_pitch:
			AP_pitch = False
			#elevtrim_pos.value = 0
			sevent.eventlist.list[1].send()
			
		else:
			AP_pitch = True
			#pitch_PID.I = (elev_trim.value * 16000 / 10000) / pitch_PID.Kp
			#pitch_PID.Ref = IAS.value / 100.0
			#pitch_PID.prev_error = 0.0
			pitch_PID.turn_on(pitch.value)
			VS_PID.turn_on(vs.value/ 1000.0)
	elif c == ord('b'):
		if AP_bank:
			AP_bank = False
			aileron_pos.value = 0
			sevent.eventlist.list[0].send()
		else:
			AP_bank = True
			bank_PID.turn_on(bank.value)
			#heading_PID.turn_on(
			#bank_PID.u = 0.0
			#bank_PID.I = 0.0
	elif c == 56: #Up arrow
			pitch_ref = pitch_ref + 0.1
			VS_ref = VS_ref + 0.1
	elif c == 50: #Down arrow
			pitch_ref = pitch_ref - 0.1
			VS_ref = VS_ref - 0.1
	elif c == 54: #Up arrow
			bank_ref -= 1.0
	elif c == 52: #Down arrow
			bank_ref += 1.0
	elif c == ord('a'):
			data.Kp -= step
	elif c == ord('q'):
			data.Kp += step
	elif c == ord('s'):
			data.Ti -= step
	elif c == ord('w'):
			data.Ti += step
	elif c == ord('d'):
			data.Td -= step
	elif c == ord('e'):
			data.Td += step
	elif c == ord('f'):
			data.Roc -= step
	elif c == ord('r'):
			data.Roc += step		
	elif c == ord('='):
			step *= 10
	elif c == ord('-'):
			step *= 0.1

	stdscr.addstr(10,10, "%d" %c)
	stdscr.refresh()
	
	
	
aileron_pos.value = 0
sevent.eventlist.list[0].send()
s.close()
curses.endwin()
print time.time() - start_time
f.close()