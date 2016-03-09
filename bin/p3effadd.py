#!/usr/bin/env python

import os
import sys
import argparse

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <input>
	Add parameters into the input .eff files.
	"""
	
	args_def = {'add':'restrain_planarity = True'}	
	parser = argparse.ArgumentParser()
	parser.add_argument("eff", nargs='*', help="specify .eff files to be processed")
	parser.add_argument("-a", "--add", type=str, help="specify what to add, by default '{}'. You may also need 'planarity_sigma = 0.001'.".format(args_def['add']))
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
	for eff in args.eff:
		basename = os.path.basename(os.path.splitext(eff)[0])
		with open(eff) as e_read:
			lines = e_read.readlines()
		with open(basename+'_zz.eff', 'w') as e_write:
			j = 0
			for i, line in enumerate(lines):
				e_write.write(line)
				if line == '      base_pair {\n':
					j = 1
				if j == 1 and lines[i+1] == '      }\n':
					e_write.write("        " + args.add+'\n')
					j = 0
				
if __name__ == '__main__':
	main()
