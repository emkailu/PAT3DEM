#!/usr/bin/env python

import os
import sys
import argparse
from EMAN2 import *
import pat3dem.pdb as p3p

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <pdbs>
	Calculate ccc between pdb and mrc
	"""
	
	args_def = {'mrc':'', 'res':6}	
	parser = argparse.ArgumentParser()
	parser.add_argument("pdbs", nargs='*', help="specify pdbs to be processed")
	parser.add_argument("-m", "--mrc", type=str, help="specify mrc, by default {}".format(args_def['mrc']))
	parser.add_argument("-r", "--res", type=float, help="specify resolution, by default {}".format(args_def['res']))
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
	d = EMData(args.mrc)
	boxsize = d["nx"]
	apix = d["apix_x"]
	for i in args.pdbs:
		pa=PointArray()
		pa.read_from_pdb(i)
		out=pa.pdb2mrc_by_summation(boxsize,apix,args.res,-1)
		c = d.cmp("ccc",out)
		print i,c
		
if __name__ == '__main__':
	main()
