#!/usr/bin/env python

import os
import sys
import argparse
from EMAN2 import *
import pat3dem.main as p3m

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <image>
	Generate a cuboid on the grid of input image.
	"""
	
	args_def = {'increment':-1, 'coord':'-1 '*6}
	parser = argparse.ArgumentParser()
	parser.add_argument("image", nargs='*', help="specify an image")
	parser.add_argument("-i", "--increment", type=int, help="specify an increment for grids (for initial location), by default {}, which means do not generate grids".format(args_def['increment']))
	parser.add_argument("-c", "--coord", type=str, help="specify a coordinate range, 'x1 x2 y1 y2 z1 z2', by default '{}', which means do not generate a cuboid".format(args_def['coord']))
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
	image = args.image[0]
	d = EMData(image)
	i = args.increment
	if i != -1:
		edge = d.get_xsize() / i
		for x in xrange(edge):
			for y in xrange(edge):
				for z in xrange(edge):
					d.set_value_at(x*i,y*i,z*i,100 + x*x+y*y+z*z)
	if args.coord != '-1 '*6:
		p3m.set_value(d, args.coord, 100)
	x1, x2, y1, y2, z1, z2 = p3m.get_coord(args.coord)
	d.write_image(image[:-4]+"_cuboid_{}-{}_{}-{}_{}-{}.mrc".format(x1, x2, y1, y2, z1, z2))		
	
if __name__ == '__main__':
	main()
