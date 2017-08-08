#!/usr/bin/env python

import os
import sys
import argparse
import random
from EMAN2 import *

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <*.mrc>
	Process input.
	"""
	
	args_def = {'repeat':1}	
	parser = argparse.ArgumentParser()
	parser.add_argument("mrc", nargs='*', help="specify input to be processed")
	parser.add_argument("-r", "--repeat", type=int, help="specify repeat times, by default {}".format(args_def['repeat']))
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
	for mrc in args.mrc:
		d=EMData(mrc)
		for i in range(args.repeat):
			e=d
			e.transform(Transform({'n1':1,'n2':1,'n3':1, 'omega':random.randint(-10,10), 'tx':0.00,'ty':0.00,'tz':0.00,'mirror':0,'scale':1.0000,'type':'spin'}))
			e.write_image('{}.mrc'.format(i))
				
if __name__ == '__main__':
	main()
