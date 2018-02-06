#!/usr/bin/env python

import os
import sys
import argparse
import math

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <shifts.txt>
	Check the drift output by unblur.
	The drift between two adjacent frames are unrealistically big.
	"""
	
	args_def = {'target':5}
	parser = argparse.ArgumentParser()
	parser.add_argument("log", nargs='*', help="specify the shifts.txt files by unblur")
	parser.add_argument("-t", "--target", type=float, help="specify target resolution in Angstrom, by default {}".format(args_def['target']))
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
	with open('zz_frame-mic-shift.txt', 'w') as drift:
		mic = 0
		for log in args.log:
			mic += 1
			with open(log) as log_r:
				lines = [line for line in log_r]
			xline = lines[-2].strip().split()
			yline = lines[-1].strip().split()
			x0 = float(xline.pop(0))
			y0 = float(yline.pop(0))		
			f = 1
			while len(xline) > 0:
				x = float(xline.pop(0))
				y = float(yline.pop(0))
				dis = math.sqrt((x - x0)**2 + (y - y0)**2)
				if dis >args.target:
					dis = args.target
				drift.write('{} {} {}\n'.format(f, mic, dis))
				f += 1
				x0 = x
				y0 = y
		
if __name__ == '__main__':
	main()
