#!/usr/bin/env python

import os
import sys
import argparse
import scipy.optimize as opt
from EMAN2 import *

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <map1 map2>
	Change the apix of map1 based on map2. They have to be roughly aligned. They can be aligned and resampled in Chimera (vop resample #map1 ongrid #map2, the apix of map1 will become the same as map2, but the ratio between nominal apix and true apix does not change).
	"""
	
	args_def = {'apix':1}	
	parser = argparse.ArgumentParser()
	parser.add_argument("maps", nargs='*', help="specify map1 map2 to be processed")
	parser.add_argument("-a", "--apix", type=float, help="specify apix of map2, by default {}".format(args_def['apix']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# get common parameters
	c_p = {'m1':EMData(args.maps[0]), 'm2':EMData(args.maps[1]), 'apix':args.apix}
	c_p['boxsize'] = c_p['m2']["nx"]
	# run apix optimization
	f = lambda x: ccc(x, c_p)
	rranges = [slice(args.apix-0.05, args.apix+0.05, 0.005)]
	resbrute = opt.brute(f, rranges, full_output=True, finish=opt.fmin)
	x_res, y_res = resbrute[0][0], resbrute[1]
	print x_res, y_res
	
def ccc(x, c_p):
	ali=ccc_align(x, c_p)
	score = ali['score']
	print float(x), score
	return score

def ccc_align(x, c_p):
	# now the apix is assumed to be x
	s = float(x)/c_p['apix']
	# scale apix
	m1 = c_p['m1']
	m1 = m1.process('xform.scale',{'clip':c_p['boxsize'], 'scale':s})
	m2 = c_p['m2']
	ali=m1.align('refine_3d',m2,{},'ccc',{})
	return ali
	
if __name__ == '__main__':
	main()
