#!/usr/bin/env python

import os
import sys
import argparse
import pat3dem.pdb as p3p

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <pdbbig, pdbfrag>
	Merge pdb
	"""
	
	args_def = {'ranges':''}	
	parser = argparse.ArgumentParser()
	parser.add_argument("pdbs", nargs='*', help="specify pdbbig, pdbfrag to be processed")
	parser.add_argument("-r", "--ranges", type=str, help="specify ranges, like B8-19, by default {}".format(args_def['ranges']))
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
	chain =args.ranges[0]
	seq = args.ranges[1:].split('-')
	start, end = int(seq[0]), int(seq[1])
	mlines = p3p.pdb_merge(args.pdbs[0], args.pdbs[1], chain, start, end)
	with open('{}_merged.pdb'.format(args.pdbs[0][:-4]), 'w') as merge:
		merge.write(''.join(mlines))
							
if __name__ == '__main__':
	main()
