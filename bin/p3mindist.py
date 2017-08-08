#!/usr/bin/env python

import os
import sys
import math
import argparse
import pat3dem.pdb as p3p

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <2 pdb>
	Process input.
	"""
	
	args_def = {'chain1':'A', 'chain2':'A', 'CAonly':'0'}	
	parser = argparse.ArgumentParser()
	parser.add_argument("pdb", nargs='*', help="specify 2 pdb to be processed")
	parser.add_argument("-c1", "--chain1", type=str, help="specify chain of the first pdb, by default {}".format(args_def['chain1']))
	parser.add_argument("-c2", "--chain2", type=str, help="specify chain of the second pdb, by default {}".format(args_def['chain2']))
	parser.add_argument("-ca", "--CAonly", type=str, help="specify as 1 if you want CAonly, by default {}".format(args_def['CAonly']))
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
	min2 = 10000
	I = ()
	J = ()
	coord1 = pdb2list(args.pdb[0], args.chain1, args.CAonly)
	coord2 = pdb2list(args.pdb[1], args.chain2, args.CAonly)
	for i in coord1:
		for j in coord2:
			d2 = (i[0]-j[0])*(i[0]-j[0]) + (i[1]-j[1])*(i[1]-j[1]) + (i[2]-j[2])*(i[2]-j[2])
			if d2 < min2:
				min2=d2
				I = i
				J = j
	print math.sqrt(min2), I, J
	
def pdb2list(pdb,chain,ca):
	coord = []
	if ca == '1':
		lines = p3p.pdb_CA(pdb)[0]
	else:
		with open(pdb) as pdb_r:
			lines=pdb_r.readlines()
	for line in lines:
		if line[0:4] in ['ATOM', 'HETATM'] and line[21] == chain:
			coord += [p3p.get_coord(line)]
	return coord
			 
if __name__ == '__main__':
	main()
