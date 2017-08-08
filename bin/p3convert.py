#!/usr/bin/env python

import os
import sys
import argparse
import subprocess
from shutil import copyfile

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <*.png>
	convert -average *.png output.png
	In total 210 images, first average 15, then 14.
	"""
	
	args_def = {}	
	parser = argparse.ArgumentParser()
	parser.add_argument("png", nargs='*', help="specify png to be averaged")
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
	for i in xrange(14):
		cmd = ['convert', '-average'] + args.png[15*i:15*(i+1)] + ['output_{}.png'.format(i)]
		subprocess.call(cmd, stderr=subprocess.STDOUT)
	cmd = ['convert', '-average', 'output_*.png', 'output.png']
	subprocess.call(cmd, stderr=subprocess.STDOUT)
				
if __name__ == '__main__':
	main()
