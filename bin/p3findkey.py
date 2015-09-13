#!/usr/bin/env python

import os
import sys
import argparse

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <files>
	find the files that contain a key word (usually for jobstatus, 'Exited with exit code')
	optionally output the lines (of previously found files) containing a second key word (the first line for each file)
	"""
	
	args_def = {'key':'Exited with exit code', 'key2':'0'}	
	parser = argparse.ArgumentParser()
	parser.add_argument("files", nargs='*', help="specify files")
	parser.add_argument("-k", "--key", type=str, help="specify a key word, by default '{}'".format(args_def['key']))
	parser.add_argument("-k2", "--key2", type=str, help="specify a second key word, by default '{}', which means does not output lines".format(args_def['key2']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options"
		sys.exit(1)	
	else:
		# get default values
		for i in args_def:
			if args.__dict__[i] == None:
				args.__dict__[i] = args_def[i]
		# loop over files
		print "The following files contain '{}':".format(args.key)
		out = []
		for i in args.files:
			with open(i) as f:
				if args.key in f.read():
					print i
					out += [i]
		# find the lines
		if args.key2 != '0':
			print "\nThe following lines contain '{}':".format(args.key2)
			o_lines = []
			for j in out:
				with open(j) as f2:
					lines = f2.readlines()
					for line in lines:
						if args.key2 in line:
							o_lines += [line]
							break
			print ''.join(o_lines)
						
if __name__ == '__main__':
	main()
