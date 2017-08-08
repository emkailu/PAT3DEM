#!/usr/bin/env python

import os
import sys
import argparse
import math
import pat3dem.pdb as p3p

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <2 .ATOM.pdb>
	Get arrow.bild from 2 pdb.
	"""
	
	args_def = {'scale':1}	
	parser = argparse.ArgumentParser()
	parser.add_argument("pdb", nargs='*', help="specify 2 pdb (only containing ATOM) to be processed")
	parser.add_argument("-s", "--scale", type=float, help="specify scaling factor by which the end point will be changed, by default {}".format(args_def['scale']))
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
	with open(args.pdb[0]) as pdb1:
		lines1 = pdb1.readlines()
	with open(args.pdb[1]) as pdb2:
		lines2 = pdb2.readlines()
	basename = os.path.basename(os.path.splitext(args.pdb[0])[0])
	out = '{}_arrow_s{}.bild'.format(basename, args.scale)	
	with open(out,'w') as o:
		for i, line1 in enumerate(lines1):
			x1, y1, z1 = p3p.get_coord(line1)
			x2, y2, z2 = p3p.get_coord(lines2[i])
			if x1 != x2:
				x2, y2, z2 = scale(x1,x2,args.scale),scale(y1,y2,args.scale),scale(z1,z2,args.scale),
				o.write('.arrow {} {} {} {} {} {} 0.5 1.5\n'.format(x1, y1, z1, x2, y2, z2))
			else:
				o.write('\n')

def scale(x1, x2, s):
	x1, x2 = float(x1), float(x2)
	return x1 + (x2-x1)*s
				
if __name__ == '__main__':
	main()
