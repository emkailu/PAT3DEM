#!/usr/bin/env python

import os
import sys
import argparse
import time
import pat3dem.cluster as p3c

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <d.txt>
	Download the file listed in the first line of d.txt, whenever the local disk is not full. Then overwrite d.txt with following lines.
	Need to define:
	export DATA_SERVER= DATA_SERVER_USER= DATA_SERVER_PASSWORD= DATA_PATH=
	Note line_of_d.txt may include folder, as long as $DATA_PATH/line_of_d.txt is the absolute path of a file.
	"""
	
	args_def = {}	
	parser = argparse.ArgumentParser()
	parser.add_argument("f", nargs='*', help="specify a txt file, each line contains the path of a file on remote server")
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# get common parameters
	c_p = {'s':os.environ['DATA_SERVER'], 'u':os.environ['DATA_SERVER_USER'], 'p':os.environ['DATA_SERVER_PASSWORD'], 'dp':os.environ['DATA_PATH']}
	'''
	# wait until local disk and nfile are enough
	disk, nfile = p3c.ada_quota()
	while disk < 200 or nfile < 1000:
		time.sleep(600)
		disk, nfile = p3c.ada_quota()
	'''
	# get the file name	
	with open(args.f[0]) as f:
		lines = f.readlines()
	i = lines[0]
	i = i.strip()
	# download from data server, only if file does not exist
	if not os.path.isfile(i):
		fd = os.path.dirname(i)
		if fd:
			if not os.path.exists(fd):
				os.makedirs(fd)		
		p3c.server_download(i, i, c_p)
		# overwrite d.txt
		if len(lines) > 1:
			with open(args.f[0], 'w') as f:
				f.write(''.join(lines[1:]))

if __name__ == '__main__':
	main()
