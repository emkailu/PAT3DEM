#!/usr/bin/env python

import os
import sys
import argparse
import pat3dem.cluster as p3c
			
def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <movie.mrcs>
	Run p3ctf.py on cluster.
	Needs:
	ctffind (v4.0.16, Rohou & Grigorieff, 2015)
	"""
	
	args_def = {'apix':1.25, 'voltage':200, 'cs':2, 'ac':0.1, 'dpsize':5}	
	parser = argparse.ArgumentParser()
	parser.add_argument("image", nargs='*', help="specify images to be processed")
	parser.add_argument("-a", "--apix", type=float, help="specify apix, by default {}".format(args_def['apix']))
	parser.add_argument("-v", "--voltage", type=int, help="specify the voltage (kV), by default {}".format(args_def['voltage']))
	parser.add_argument("-c", "--cs", type=float, help="specify spherical abberration, by default {}".format(args_def['cs']))
	parser.add_argument("-ac", "--ac", type=float, help="specify amplitude contrast, by default {}".format(args_def['ac']))
	parser.add_argument("-d", "--dpsize", type=float, help="specify detector pixel size (um), by default {}".format(args_def['dpsize']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# loop over all the input images
	for image in args.image:
		basename = os.path.basename(os.path.splitext(image)[0])
		cmd = "p3ctf.py {} -a {} -v {} -c {} -ac {} -d {}".format(image, args.apix, args.voltage, args.cs, args.ac, args.dpsize)
		walltime, cpu, ptile = 1, 1, 1
		p3c.ada(cmd, basename, walltime, cpu, ptile)		
		
if __name__ == '__main__':
	main()
