#!/usr/bin/env python

import os
import sys
import argparse
import math
import pat3dem.pdb as p3p

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <pdbs>
	Output the pdb name, and the sum of CA deviation between the pdb and the native pdb.
	"""
	
	args_def = {'native':''}
	parser = argparse.ArgumentParser()
	parser.add_argument("pdb", nargs='*', help="specify aligned pdb files")
	parser.add_argument("-n", "--native", type=str, help="specify the native pdb, by default {}".format(args_def['native']))
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
	pdbn_CA, pdbn_CA27 = p3p.pdb_CA(args.native)
	for i in args.pdb:
		devsum = 0
		pdbi_CA, pdbi_CA27 = p3p.pdb_CA(i)
		pdb_same = set(pdbn_CA27).intersection(pdbi_CA27)
		for j in pdbn_CA:
			if j[17:27] in pdb_same:
				for k in pdbi_CA:
					if k[17:27] == j[17:27]:break
				(x1, y1, z1), (x2, y2, z2) = p3p.get_coord(j), p3p.get_coord(k)
				dev = math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)
				devsum += dev
		print i, devsum
    
if __name__ == '__main__':
	main()
    