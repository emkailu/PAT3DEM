#!/usr/bin/env python

import os
import sys
import argparse
import time
import pat3dem.cluster as p3c

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <f.txt>
	download the files listed in f.txt, whenever the local disk is not full
	"""
	
	args_def = {'password':'/home/kailuyang/.pp'}	
	parser = argparse.ArgumentParser()
	parser.add_argument("f", nargs='*', help="specify a txt file, each line contains the path of a file on remote server")
	parser.add_argument("-p", "--password", type=str, help="specify the file containing password, by default '{}'".format(args_def['password']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options"
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# get common parameters
	with open(args.password) as f:
		p = f.read().strip()
	com_par = {'p':p}
	# download from chiu to ada		
	with open(args.f[0]) as f:
		lines = f.readlines()
	for i in lines:
		# wait until local disk and nfile are enough
		disk, nfile = p3c.ada_quota()
		while disk < 200 or nfile < 1000:
			time.sleep(600)
			disk, nfile = p3c.ada_quota()
		i = i.strip()
		j = './' + i.replace('\\','/').split('/')[-1]
		p3c.chiu_download(i, j, com_par)
	
if __name__ == '__main__':
	main()
