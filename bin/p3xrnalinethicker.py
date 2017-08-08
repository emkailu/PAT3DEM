#!/usr/bin/env python

import os
import sys
import argparse

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <.xrna>
	Change the line width in .xrna.
	"""
	
	args_def = {'width':0.5}	
	parser = argparse.ArgumentParser()
	parser.add_argument("xrna", nargs='*', help="specify .xrna to be processed")
	parser.add_argument("-w", "--width", type=float, help="specify line width, by default {}".format(args_def['width']))
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
	for xrna in args.xrna:
		with open(xrna) as xrna_old:
			lines = xrna_old.readlines()
		basename = os.path.basename(os.path.splitext(xrna)[0])
		with open('{}_linewidth{}.xrna'.format(basename,args.width),'w') as xrna_new:
			for line in lines:
				if line == '':
					xrna_new.write(line)
				elif line[0] != 'l':
					xrna_new.write(line)
				else:
					line = line.split()
					line[5] = str(args.width)
					line_new = ' '.join(line)
					xrna_new.write(line_new + '\n')
				
if __name__ == '__main__':
	main()
