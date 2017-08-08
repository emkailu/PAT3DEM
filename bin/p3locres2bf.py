#!/usr/bin/env python

import os
import sys
import argparse
from EMAN2 import *
import pat3dem.pdb as p3p
import pat3dem.main as p3m

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <localres.mrc>
	Get local resolution from localres.mrc and transfer to bfactors in pdb.
	"""
	
	args_def = {'apix':1.25, 'pdb':''}	
	parser = argparse.ArgumentParser()
	parser.add_argument("mrc", nargs='*', help="specify localres.mrc to be processed")
	parser.add_argument("-a", "--apix", type=float, help="specify apix, by default {}".format(args_def['apix']))
	parser.add_argument("-p", "--pdb", type=str, help="specify the pdb, by default {}".format(args_def['pdb']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# read the pdb
	with open(args.pdb) as p:
		lines = p.readlines()
	ATM = []
	for i in lines:
		if i[:4] == 'ATOM' or i[:6] == 'HETATM': 
			ATM += [i]	
	basename = os.path.basename(os.path.splitext(args.pdb)[0])
	a = args.apix
	with open(basename + '_locres2bf.pdb', 'w') as w_pdb:
		d = EMData(args.mrc[0])
		for i in ATM:
			(x, y, z) = p3p.get_coord(i)
			x, y, z = int(x/a), int(y/a), int(z/a)
			res = d.get_value_at(x, y, z)
			i = list(i)
			i[60:66] = '{:6.2f}'.format(res)
			w_pdb.write(''.join(i))	
			
if __name__ == '__main__':
	main()
