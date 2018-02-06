#!/usr/bin/env python

import os
import sys
import argparse
import math

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <motioncor2run.log>
	Check the following errors:
	1. The global alignment did not go smaller than 0.5 within specified iterations.
	2. The local alignment did not go smaller than 0.5 even after using a larger patch size.
	The input is the run log on one movie stack.
	"""
	
	args_def = {}
	parser = argparse.ArgumentParser()
	parser.add_argument("log", nargs='*', help="specify the run log files")
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# loop through the log files
	for log in args.log:
		with open(log) as log_r:
			lines = [line for line in log_r]
		error = -1 # initialize as -1 to recognize the first error, i.e., global
		while len(lines) > 0:
			line1 = lines.pop(0)				
			if "Total Iterations:" in line1:
				line = line1.split()
				error_new = float(line[-1])
				if error_new > 0.5:
					if error == -1:
						print "Global: {}: {}".format(log,lines[1].strip())
						break
					elif error > 0.5:
						print "Local: {}: {}".format(log,lines[1].strip())
						break
				error = error_new
				
if __name__ == '__main__':
	main()
