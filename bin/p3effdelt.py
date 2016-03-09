#!/usr/bin/env python

import os
import sys
import argparse

def gothr(lines):
	if lines[0] not in ['      base_pair {\n', '      stacking_pair {\n']:
		return lines[0:1], lines[1:]
	else:
		for i, line in enumerate(lines):
			if line == '      }\n':
				return lines[:i+1], lines[i+1:]

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <input>
	Delete some residues in the input .eff files.
	"""
	
	args_def = {'delt':'0 10001', 'drange':'0 0'}	
	parser = argparse.ArgumentParser()
	parser.add_argument("eff", nargs='*', help="specify .eff files to be processed")
	parser.add_argument("-d", "--delt", type=str, help="specify what to delete, by default '{}'".format(args_def['delt']))
	parser.add_argument("-dr", "--drange", type=str, help="specify a range to delete, by default '{}'".format(args_def['drange']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# loop over all the input eff
	delt = args.delt.split()
	drange = args.drange.split()
	for i in xrange(int(drange[0]), int(drange[1])):
		delt += [str(i)]
	for eff in args.eff:
		basename = os.path.basename(os.path.splitext(eff)[0])
		with open(eff) as e_read:
			lines = e_read.readlines()
		with open(basename+'_delt.eff', 'w') as e_write:
			while len(lines) > 0:
				l, lines = gothr(lines)
				if len(l) == 1:
					e_write.write(''.join(l))
				else:
					p1 = l[1].split()[-1]
					p2 = l[2].split()[-1]
					if p1 not in delt and p2 not in delt:
						e_write.write(''.join(l))
					else:
						print 'Deleting:\n' + ''.join(l)
						
if __name__ == '__main__':
	main()
