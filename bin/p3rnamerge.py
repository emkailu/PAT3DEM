#!/usr/bin/env python

import os
import sys
import argparse

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <pdb files>
	Use ModeRNA to merge RNA fragments. What's the best way to ensure good connectivity?!
	Real case: you have two pdb files, p1 and p2. p1 is better than p2, but p1 is not complete. p2 may not be complete either, but it contains the missing parts in p1.
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
	# this is an example script. please follow the format
	print "This is an example script. Please follow the format."
	
				
if __name__ == '__main__':
	main()
