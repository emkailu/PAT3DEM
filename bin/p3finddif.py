#!/usr/bin/env python

import os
import sys
import argparse

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <file1 and file2>
	compare file1 and file2, line by line (usually com/log/star files)
	output the lines that are different in file1 and file2
	"""
	
	args_def = {}	
	parser = argparse.ArgumentParser()
	parser.add_argument("files", nargs='*', help="specify 2 files to be compared")
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
		#		
		file1, file2 = args.files
		with open(file1) as f1:
			with open(file2) as f2:
				lines1 = f1.readlines()
				lines2 = f2.readlines()
				if lines1 != lines2:
					print file1, '!=', file2
					for i, line1 in enumerate(lines1):
						try:
							line2 = lines2[i]
						except IndexError:
							sys.exit('file2 is shorter, further comparison makes no sense')
						if line1 != line2:
							print '*'*30
							print 'In line {}:\n'.format(i), line1, line2
							
if __name__ == '__main__':
	main()
