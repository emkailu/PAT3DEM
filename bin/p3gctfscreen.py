#!/usr/bin/env python

import os
import sys
import argparse

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <_gctf.log>
	Screen based on the output of gctf.
	"""
	
	args_def = {'cutoff':10}	
	parser = argparse.ArgumentParser()
	parser.add_argument("ctfout", nargs='*', help="specify _gctf.log to be screened")
	parser.add_argument("-c", "--cutoff", type=float, help="specify cutoff of RES_LIMIT, by default {}".format(args_def['cutoff']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# loop over
	for ctfout in args.ctfout:
		with open(ctfout) as ctf_read:
			lines = ctf_read.readlines()
		res_limit = float(lines[-3].split()[-1])
		if res_limit > args.cutoff:
			print ctfout		
			
if __name__ == '__main__':
	main()
