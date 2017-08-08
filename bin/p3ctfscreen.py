#!/usr/bin/env python

import os
import sys
import argparse

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <ctfout.txt or _ctffind3.log>
	Screen based on the output of p3ctf.py.
	If there is no '_ctffind3.log', you may need to rerun, manually check the quality and/or move it to bad/ folder.
	Then use this script to check if the maxres or the best Thon ring is too low.
	"""
	
	args_def = {'cutoff':10}	
	parser = argparse.ArgumentParser()
	parser.add_argument("ctfout", nargs='*', help="specify ctf output.txt or _ctffind3.log to be screened")
	parser.add_argument("-c", "--cutoff", type=float, help="specify cutoff of maxres and best ring, by default {}".format(args_def['cutoff']))
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
	if args.ctfout[0][-4:] == '.txt':
		for ctfout in args.ctfout:
			with open(ctfout) as ctf_read:
				lines = ctf_read.readlines()
			maxres = float(lines[3].replace(';', '').split()[9])
			best_ring = float(lines[5].split()[6])
			if maxres > args.cutoff or best_ring > args.cutoff:
				print ctfout		
	elif 	args.ctfout[0][-13:] == '_ctffind3.log':	
		for ctfout in args.ctfout:
			with open(ctfout) as ctf_read:
				lines = ctf_read.readlines()
			for i in lines:
				if "Thon rings with good fit up to" in i:
					best_ring = float(i.split()[-2])
			if best_ring < args.cutoff:
				print ctfout		
if __name__ == '__main__':
	main()
