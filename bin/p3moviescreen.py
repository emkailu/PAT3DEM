#!/usr/bin/env python

import os
import sys
import argparse

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <_unblur.log>
	Screen based on the output of p3movie.py.
	"""
	
	args_def = {'cutoff':1}
	parser = argparse.ArgumentParser()
	parser.add_argument("unblur", nargs='*', help="specify all the _unblur.log to be screened")
	parser.add_argument("-c", "--cutoff", type=float, help="specify cutoff of 'Average X/Y shift' in angstrom, by default {}".format(args_def['cutoff']))
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
	for unblur in args.unblur:
		with open(unblur) as unblur_read:
			lines = unblur_read.readlines()
		shift_X = float(lines[-6].replace(':', ' ').split()[-2])
		shift_Y = float(lines[-7].replace(':', ' ').split()[-2])
		if shift_X > args.cutoff or shift_Y > args.cutoff:
			print unblur
			
if __name__ == '__main__':
	main()
