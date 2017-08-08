#!/usr/bin/env python

import os
import sys
import argparse
from moderna import *

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <rna.pdb>
        Run modeRNA to clean the pdb.
        Needs:
        ModeRNA (v1.7.1, Rother et al., 2011)
        """
	
	args_def = {'chain':'A'}	
	parser = argparse.ArgumentParser()
	parser.add_argument("pdb", nargs='*', help="specify the rna pdbs.")
	parser.add_argument("-c", "--chain", type=str, help="specify chains, by default {}".format(args_def['chain']))
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
	for i in args.pdb:
		base_pdb = os.path.basename(os.path.splitext(i)[0])
		rmmd = base_pdb + '_clean.pdb'
		with open(rmmd, 'a') as rmmda:
			for j in list(args.chain):
				m = load_model(i,j)
				clean_structure(m)
				remove_all_modifications(m)
				rmmdj = rmmd+j
				m.write_pdb_file(rmmdj)
				with open(rmmdj) as jr:
					f = jr.readlines()
				os.remove(rmmdj)
				rmmda.write(''.join(f[:-1]))
			rmmda.write('END\n')
	    
if __name__ == '__main__':
	main()
