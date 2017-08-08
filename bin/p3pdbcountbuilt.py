#!/usr/bin/env python

import os
import sys
import argparse
import pat3dem.pdb as p3p
import string

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <pdbs>
	Given pdb files, report the built residues in csv files.
	"""
	
	args_def = {}	
	parser = argparse.ArgumentParser()
	parser.add_argument("pdb", nargs='*', help="specify pdbs to be processed")
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
	for pdb in args.pdb:
		with open(pdb) as read_pdb:
			lines = read_pdb.readlines()	
		chain = {} # {chainX:[(num, res)]}
		N = 0 # res num
		C = '' # chain id
		for i in lines:
			if i[:4].strip() in ['ATOM']:
				c = i[21]
				if C != c: # different chain id, reset res num as 0
					C = c
					N = 0
				n = int(i[22:26])
				if N != n:
					N = n
					chain[c] = chain.get(c, []) + [(n, p3p.aa_3to1(i[17:20]))]
		basename = os.path.basename(os.path.splitext(pdb)[0])
		with open(basename+'_built-residues.csv', 'w') as out:
			for j in sorted(chain):
				grouped = list(group(chain[j]))
				final = repr(grouped).replace('[(', '').replace(')]', '').replace('), (', ';').replace(', ', '-')
				out.write('{},{}\n'.format(j,final))
					
def group(L):
	first = last = L[0][0]
	for N in L[1:]:
		n = N[0]
		if n - 1 == last: # Part of the group, bump the end
			last = n
		else: # Not part of the group, yield current group and start a new
			yield first, last
			first = last = n
	yield first, last # Yield the last group
				
if __name__ == '__main__':
	main()
