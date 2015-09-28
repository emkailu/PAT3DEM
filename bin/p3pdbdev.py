#!/usr/bin/env python

import os
import sys
import argparse
import math
import pat3dem.pdb as p3p

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <pdb1, pdb2>
	output pdb1, whose bfactor is replaced by CA deviation between pdb1 and pdb2
	"""
	
	args_def = {}
	parser = argparse.ArgumentParser()
	parser.add_argument("pdb", nargs='*', help="specify two aligned pdb files")
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options"
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	#
	if len(args.pdb) != 2:
		sys.exit('Please input two pdb files!')
	pdb1, pdb2 = args.pdb
	pdb1_CA, pdb1_CA27 = p3p.pdb_CA(pdb1)
	pdb2_CA, pdb2_CA27 = p3p.pdb_CA(pdb2)
	pdb_same = set(pdb1_CA27).intersection(pdb2_CA27)
	basename1 = os.path.basename(os.path.splitext(pdb1)[0])
	basename2 = os.path.basename(os.path.splitext(pdb2)[0])
	with open(basename1 + '_dev_' + basename2 + '.pdb', 'w') as w_pdb:
		for i in pdb1_CA:
			if i[:27] in pdb_same:
				for j in pdb2_CA:
					if j[:27] == i[:27]:break
				(x1, y1, z1), (x2, y2, z2) = p3p.get_coord(i), p3p.get_coord(j)
				dev = math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)
				i = list(i)
				i[60:66] = '{:6.2f}'.format(dev)
				w_pdb.write(''.join(i))
    
if __name__ == '__main__':
	main()
    