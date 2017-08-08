#!/usr/bin/env python

import os
import sys
import argparse
from EMAN2 import *

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <micrograph.mrc>
	Generate boxes to cover the entire micrograph. The module (micrograph size % box size) will be treaded as edge.
	"""
	
	args_def = {'boxsize':120, 'overlap':0}
	parser = argparse.ArgumentParser()
	parser.add_argument("mic", help="specify a micrograph to be processed")
	parser.add_argument("-b", "--boxsize", type=int, help="specify boxsize, by default {}".format(args_def['boxsize']))
	parser.add_argument("-o", "--overlap", type=int, help="specify the overlap between two neighbouring boxes, by default {}".format(args_def['overlap']))
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
	d = EMData(args.mic)
	X = d["nx"]
	Y = d["ny"]
	box = args.boxsize
	interval = box-args.overlap
	modX = X % interval
	modY = Y % interval
	edgeX = modX/2 - args.overlap/2
	edgeY = modY/2 - args.overlap/2
	with open(args.mic+'.box', 'w') as box_w:
		for x in xrange(X/interval):
			for y in xrange(Y/interval):
				box_w.write('{} {} {} {}\n'.format(x*interval+edgeX, y*interval+edgeY, box, box))
	
if __name__ == '__main__':
	main()
