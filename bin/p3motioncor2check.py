#!/usr/bin/env python

import os
import sys
import argparse
import math

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <motioncor2run.log>
	Check the shift measured by MotionCor2. Usually there are two errors to check:
	1. The shift between two adjacent frames are unrealistically big or simply bigger than the target resolution.
	2. The patch alignment did not go smaller than 0.5 even after using a larger patch size. (Not implemented yet)
	The input is the run log on one movie stack.
	"""
	
	args_def = {'apix':0.615, 'target':5}
	parser = argparse.ArgumentParser()
	parser.add_argument("log", nargs='*', help="specify the run log files")
	parser.add_argument("-a", "--apix", type=float, help="specify apix of the input stack to run motioncor2, by default {}".format(args_def['apix']))
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
			x0 = 0
			y0 = 0
			f = 0
			while len(lines) > 0:
				line1 = lines.pop(0)
				if "illegal memory access" in line1:
					continue;continue				
				if "...... Frame (" in line1:
					line = line1.strip().split()
					x = float(line[-2])
					y = float(line[-1])
					dis = math.sqrt((x - x0)**2 + (y - y0)**2) * args.apix
					if dis  > args.target:
						dis = args.target
					if f > 0:
						drift.write('{} {} {}\n'.format(f, mic, dis))
					f += 1
					x0 = x
					y0 = y
	# plot
	import numpy as np
	import matplotlib.pyplot as plt
	
	x,y,temp = np.loadtxt('zz_frame-mic-shift.txt').T #Transposed for easier unpacking
	nrows, ncols = len(args.log),f-1
	grid = temp.reshape((nrows, ncols))
	
	np.savetxt('zz_grid.txt', grid, delimiter=',')
	
	my_dpi=92
	
	fig, ax = plt.subplots(figsize=(nrows/10,ncols/10))
	im = ax.imshow(grid.T, interpolation='nearest')
	fig.colorbar(im)
	plt.savefig("zz_frame-mic-shift.png", transparent=True, dpi=my_dpi)
	plt.axis('off')
	plt.savefig("zz_frame-mic-shift_no-axis.png", transparent=True, dpi=my_dpi)
	
if __name__ == '__main__':
	main()
