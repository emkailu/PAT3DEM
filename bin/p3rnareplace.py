#!/usr/bin/env python

import os
import sys
import argparse
from moderna import *

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <*_#-#.pdb>
	Use the input fragments to replace the original rna pdb.
	"""
	
	args_def = {'pdb':''}	
	parser = argparse.ArgumentParser()
	parser.add_argument("frag", nargs='*', help="specify *_#-#.pdb")
	parser.add_argument("-p", "--pdb", type=str, help="specify the original pdb, by default {}".format(args_def['pdb']))
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
	m = load_model(args.pdb)
	new = create_model()
	copy_some_residues(m, new)
	for i in args.frag:
		# get start and end point from the file name
		r = os.path.basename(os.path.splitext(i)[0]).split('_')[-1].split('-')
		f = create_fragment(i, new[r[0]], new[r[1]])
		insert_fragment(new, f)
	basename = os.path.basename(os.path.splitext(args.pdb)[0])
	new.write_pdb_file(basename + '_replaced.pdb')
	
if __name__ == '__main__':
	main()
