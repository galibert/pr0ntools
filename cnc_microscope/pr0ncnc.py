#!/usr/bin/python
# pr0ncnc: IC die image scan
# Copyright 2011 John McMaster <johnDMcMaster@gmail.com>

import sys
import time
import math

VERSION = '0.1'

def help():
	print 'pr0ncnc version %s' % VERSION
	print 'Copyright 2011 John McMaster <JohnDMcMaster@gmail.com>'
	print 'Usage:'
	print 'pr0nstitch <x1>,<y1>,<z1> [<x2>,<y2>,<z2>]' #[<x3>,<y3>,<z3> <x4>,<y4>,<z4>]]
	print 'if one set of points specified, assume 0,0,0 forms other part of rectangle'
	print 'If two points are specified, assume those as the opposing corners'
	# maybe support later if makes sense, closer to polygon support
	# print 'If four points are specified, use those as the explicit corners'

def end_program():
	print 'M2'
	
def pause(seconds):
	print 'G4 P%d' % seconds

def take_picture():
	focus_camera()
	do_take_picture()
	reset_camera()

def focus_camera():
	print 'M7'
	pause(3)

pictures_taken = 0
def do_take_picture():
	global pictures_taken

	pictures_taken += 1
	print 'M8'
	pause(3)

def reset_camera():
	print 'M9'
	
def absolute_move(x, y, z = None):
	do_move('G90', x, y, z)

def relative_move(x, y, z = None):
	if not x and not y and not z:
		print '(omitted G91 for 0 move)'
		return
	do_move('G91', x, y, z)

def do_move(code, x, y, z):
	x_part = ''
	if x:
		x_part = ' X%lf' % (x)
	y_part = ''
	if y:
		y_part = ' Y%lf' % (y)
	z_part = ''
	if z:
		z_part = ' Z%lf' % (z)

	print '%s G1%s%s%s F3' % (code, x_part, y_part, z_part)

def drange(start, stop, step):
	r = start
	while r < stop:
		yield r
		r += step

'''
I'll move this to a JSON, XML or something format if I keep working on this

Canon SD630

15X eyepieces
	Unitron WFH15X
Objectives
	5X
	10X
	20X
	40X
	
Intel wafer
upper right: 0, 0, 0
lower left: 0.2639,0.3275,-0.0068

'''
class FocusLevel:
	# Assume XY isn't effected by Z
	eyepeice_mag = 10.0
	objective_mag = 5.0
	# Not including digital
	camera_mag = 3.0
	# Usually I don't use this, I'm not sure if its actually worth anything
	camera_digital_mag = 4.0
	# Rough estimates for now
	# The pictures it take are actually slightly larger than the view area I think
	# Inches, or w/e your measurement system is set to
	x_view = 0.0350
	y_view = 0.0465
	
	def __init__(self):
		pass

if __name__ == "__main__":
	for arg_index in range (1, len(sys.argv)):
		arg = sys.argv[arg_index]
		arg_key = None
		arg_value = None
		if arg.find("--") == 0:
			arg_value_bool = True
			if arg.find("=") > 0:
				arg_key = arg.split("=")[0][2:]
				arg_value = arg.split("=")[1]
				if arg_value == "false" or arg_value == "0" or arg_value == "no":
					arg_value_bool = False
			else:
				arg_key = arg[2:]
				
		if arg_key == "help":
			help()
			sys.exit(0)
		if arg_key == "at-optimized-parameters":
			at_optmized_parameters = arg_values
		else:
			log('Unrecognized argument: %s' % arg)
			help()
			sys.exit(1)
	
	focus = FocusLevel()
	overlap = 2.0 / 3.0
	overlap_max_error = 0.05
	
	x_min = 0.0
	y_min = 0.0
	z_start = 0.0
	x_max = 0.2639
	y_max = 0.3275
	z_end = -0.0068
	
	full_x_delta = x_max - x_min
	full_y_delta = x_max - y_min
	full_z_delta = z_end - z_start
	#print full_z_delta
	
	x_images = full_x_delta / (focus.x_view * overlap)
	y_images = full_y_delta / (focus.y_view * overlap)
	x_images = round(x_images)
	y_images = round(y_images)
	
	x_step = x_max / x_images
	y_step = y_max / y_images
	
	prev_x = 0.0
	prev_y = 0.0
	prev_z = 0.0

	print
	print
	print
	print '(Generated by pr0nstitch %s on %s)' % (VERSION, time.strftime("%d/%m/%Y %H:%M:%S"))

	# Because of the play on Z, its better to scan in same direction
	# Additionally, it doesn't matter too much for focus which direction we go, but XY is thrown off
	# So, need to make sure we are scanning same direction each time
	# err for now just easier I guess
	forward = True
	for cur_x in drange(x_min, x_max, x_step):
		for cur_y in drange(y_min, y_max, y_step):
			'''
			Until I can properly spring load the z axis, I have it rubber banded
			Also, for now assume simple planar model where we assume the third point is such that it makes the plane "level"
				That is, even X and Y distortion
			'''
			
			'''
			To find the Z on this model, find projection to center line
			Projection of A (position) onto B (center line) length = |A| cos(theta) = A dot B / |B| 
			Should I have the z component in here?  In any case it should be small compared to others 
			and I'll likely eventually need it
			'''
			print
			center_length = math.sqrt(x_max * x_max + y_max * y_max)
			projection_length = (cur_x * x_max + cur_y * y_max) / center_length
			# Proportion of entire sweep
			cur_z = full_z_delta * projection_length / center_length
			# print 'cur_z: %f, projection_length %f, center_length %f' % (cur_z, projection_length, center_length)
			# print 'full_z_delta: %f, z_start %f, z_end %f' % (full_z_delta, z_start, z_end)
			#if cur_z < z_start or cur_z > z_end:
			#	print 'cur_z: %f, z_start %f, z_end %f' % (cur_z, z_start, z_end)
			#	raise Exception('z out of range')
			x_delta = cur_x - prev_x
			y_delta = cur_y - prev_y
			z_delta = cur_z - prev_z
			
			relative_move(x_delta, y_delta, z_delta)
			take_picture()
			prev_x = cur_x
			prev_y = cur_y
			prev_z = cur_z

		'''
		if forward:
			for cur_y in range(y_min, y_max, y_step):
				inner_loop()
		else:
			for cur_y in range(y_min, y_max, y_step):
				inner_loop()
		'''
		forward = not forward

	print
	print
	print
	print '(Statistics:)'
	print '(Pictures: %d)' % pictures_taken

	end_program()
	