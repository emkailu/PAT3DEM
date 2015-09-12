#!/usr/bin/env python

import os
import sys
import argparse

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <ctfout.txt>
	screen based on the defocus value output by ctffind4
	"""
	
	parser = argparse.ArgumentParser()
	parser.add_argument("ctfout", nargs='*', help="specify ctf output.txt to be screened")
	parser.add_argument("-c", "--cutoff", type=float, help="specify cutoff, by default 2.5")
	parser.add_argument("-l", "--large", type=int, help="specify printing larger (1) or smaller (0), by default 1")
	args_default = {'cutoff':2.5, 'large':1}
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
		cutoff = args.cutoff * 10000
		if args.large == 1:
			for ctfout in args.ctfout:
				with open(ctfout) as ctf_read:
					defocus1 = float(ctf_read.readlines()[-1].split()[1])
				if defocus1 > cutoff:
					print ctfout
		else:
			for ctfout in args.ctfout:
				with open(ctfout) as ctf_read:
					defocus1 = float(ctf_read.readlines()[-1].split()[1])
				if defocus1 < cutoff:
					print ctfout
			
				
if __name__ == '__main__':
	main()
