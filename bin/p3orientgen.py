#!/usr/bin/env python

import os
import sys
import argparse
import math
from EMAN2 import *

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <input>
	Process input.
	"""
	
	args_def = {'apix':1.25, 'num':3}	
	parser = argparse.ArgumentParser()
	parser.add_argument("input", nargs='*', help="specify input to be processed")
	parser.add_argument("-a", "--apix", type=float, help="specify apix, by default {}".format(args_def['apix']))
	parser.add_argument("-n", "--num", type=int, help="specify a num, by default {}".format(args_def['num']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# 
	sym = Symmetries.get("c1")
	orients = sym.gen_orientations("eman",{"delta":10,"inc_mirror":False})
	with open('orient.com','w') as orient:
		orient.write('lighting mode single\n')
		orient.write('set bgTransparency\n\n')
		for n,i in enumerate(orients):
			alt = i.get_rotation()['alt']
			az = i.get_rotation()['az']
			x=sin_d(alt)*cos_d(az)
			y=sin_d(alt)*sin_d(az)
			z=cos_d(alt)
			orient.write('lighting key direction {:f} {:f} {:f}\n'.format(x,y,z))
			orient.write('copy file {:04d}.png png dpi 300 supersample 4 width 3000 height 3000\n\n'.format(n))

def cos_d(d):
	return math.cos(math.radians(d))
def sin_d(d):
	return math.sin(math.radians(d))
if __name__ == '__main__':
	main()
