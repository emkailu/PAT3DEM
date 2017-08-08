#!/usr/bin/env python

import os
import sys
import argparse
import pat3dem.pdb as p3p
from Bio.PDB import *

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <pdbs>
	Superimpose pdb
	"""
	
	args_def = {'fix':'','move':''}	
	parser = argparse.ArgumentParser()
	parser.add_argument("pdbs", nargs='*', help="specify pdbs to be processed")
	parser.add_argument("-f", "--fix", type=str, help="specify fixed pdb for calculating matrix, by default {}".format(args_def['fix']))
	parser.add_argument("-m", "--move", type=str, help="specify moving pdb for calculating matrix, by default {}".format(args_def['move']))
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
	sup = p3p.sup(args.fix,args.move)
	print 'rms:', sup.rms
	for i in args.pdbs:
		p = PDBParser()
		s_move = p.get_structure('move', i)
		a_move = Selection.unfold_entities(s_move, 'A')
		sup.apply(a_move)
		io = PDBIO()
		io.set_structure(s_move)
		io.save(i+'_sup.pdb')
		
if __name__ == '__main__':
	main()
