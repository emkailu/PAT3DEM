#!/usr/bin/env python

import os
import sys
import argparse

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <input>
	process input
	"""
	
	parser = argparse.ArgumentParser()
	parser.add_argument("input", nargs='*', help="specify input to be processed")
	parser.add_argument("-a", "--apix", type=float, help="specify apix, by default 1.25")
	parser.add_argument("-n", "--num", type=int, help="specify a num, by default 3")
	args_default = {'apix':1.25, 'num':3}
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options"
		sys.exit(1)	
	else:
		# get default values
		for i in args_default:
			if args.__dict__[i] == None:
				args.__dict__[i] = args_default[i]
		#		
		print args
		
				
if __name__ == '__main__':
	main()
