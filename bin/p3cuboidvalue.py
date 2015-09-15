#!/usr/bin/env python

import os
import sys
import argparse
from EMAN2 import *
import matplotlib.pyplot as plt

def get_coord(coord):
	# return 6 integers: x1, y1, z1, x2, y2, z2
	x1, y1, z1, x2, y2, z2 = coord.split()
	x1, y1, z1, x2, y2, z2 = int(x1), int(y1), int(z1), int(x2), int(y2), int(z2)
	return min(x1, x2), min(y1, y2), min(z1, z2), max(x1, x2), max(y1, y2), max(z1, z2)

def get_value(image, coord):
	# return a dictionary, {position1:value1, ..., position2:value2}
	p_dict = {}
	d = EMData(image)
	x1, y1, z1, x2, y2, z2 = get_coord(coord)
	for x in range(x1, x2+1):
		for y in range(y1, y2+1):
			for z in range(z1, z2+1):
				p_dict[(x, y, z)] = d.get_value_at(x, y, z)
	return p_dict

def plot(num):
	plt.hist(num)
	plt.title("Histogram")
	plt.xlabel("Value")
	plt.ylabel("Frequency")
	plt.savefig('zz.png')	

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <images>
	output the values of voxels within a cuboid defined by two coordinates
	needs:
	EMAN2 (v2.11, Tang et al., 2007)
	"""
	
	parser = argparse.ArgumentParser()
	parser.add_argument("image", nargs='*', help="specify images to be processed")
	parser.add_argument("-c", "--coord", type=str, help="specify 2 coordinates, by default '-1 -1 -1 -1 -1 -1 ', which means do nothing")
	args_default = {'coord':'-1 '*6}
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options"
		sys.exit(1)	
	else:
		# get default values
		for i in args_default:
			if args.__dict__[i] == None:
				args.__dict__[i] = args_default[i]
		# 
		if args.coord == '-1 '*6:
			sys.exit("What's the point if you don't specify coordinates?")
		# loop over input images, get the dictionary
		i_dict = {}
		for i in args.image:
			i_dict[i] = get_value(i, args.coord)
		# loop over the dictionary
		num = []
		for j in i_dict:
			num += i_dict[j].values()
		plot(num)
		
				
if __name__ == '__main__':
	main()
