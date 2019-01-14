#!/usr/bin/env python

import sys
from EMAN2 import *
import matplotlib.pyplot as plt

def get_coord(coord_str):
	# return the coord range, defined by the coord_str containing num and space, e.g., '8 7 1 6' will return [7, 8, 1, 6]
	c_list = coord_str.split()
	c_len = len(c_list)
	coord_range = []
	for i in xrange(c_len/2):
		num1 = int(c_list[i*2])
		num2 = int(c_list[i*2+1])
		num = [num1, num2]
		if num1 > num2:
			num = [num2, num1]
		coord_range += num
	return coord_range

def set_value(d, coord_str, value):
	# set value in d, d = EMData(image), the range is defined by coord_str
	coord_range = get_coord(coord_str)
	c_len = len(coord_range)
	if c_len == 6:
		x1, x2, y1, y2, z1, z2 = coord_range
		for x in xrange(x1, x2+1):
			for y in xrange(y1, y2+1):
				for z in xrange(z1, z2+1):
					d.set_value_at(x, y, z, value)
	else:
		sys.exit('Not 3D coordinates?!')
	return d

def get_value(image, coord_str):
	# return a dictionary, {position1:value1, ..., position2:value2}, positions are from image, and defined by coord_str
	print '\nIn {},'.format(image)
	d = EMData(image)
	p_dict = {}
	coord_range = get_coord(coord_str)
	c_len = len(coord_range)
	if c_len == 6:
		x1, x2, y1, y2, z1, z2 = coord_range
		for x in xrange(x1, x2+1):
			for y in xrange(y1, y2+1):
				for z in xrange(z1, z2+1):
					value = d.get_value_at(x, y, z)
					print '({}, {}, {}): {}'.format(x, y, z, value)
					p_dict[(x, y, z)] = value
	else:
		sys.exit('Not 3D coordinates?')
	return p_dict

def plot_hist(num_list, out):
	# read a num list, plot a histogram and save to out
	plt.hist(num_list)
	plt.title("Histogram")
	plt.xlabel("Value")
	plt.ylabel("Frequency")
	plt.savefig(out)
	plt.close()
	