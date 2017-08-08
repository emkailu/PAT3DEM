#!/usr/bin/env python

import os
import sys
import argparse
import time

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <f.txt>
	Run MotionCor2 to process movies listed in f.txt.
	"""
	
	args_def = {}
	parser = argparse.ArgumentParser()
	parser.add_argument("f", nargs='*', help="specify the txt file used for p3download.py")
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# import
	import pat3dem.cluster as p3c
	# get the local file list based on f.txt
	f = args.f[0]
	f2 = f + '.p3movie'
	with open(f) as f_r:
		lines = f_r.readlines()
	with open(f2, 'w') as f2_w:
		for i in lines:
			j = './' + i.replace('\\','/').split('/')[-1]
			f2_w.write(j)
	with open(f2) as f2_r:
		lines = f2_r.readlines()
	# run line #i if line #(i+1) exists, the last line will be ignored
	walltime, gpu, ptile = 1, 1, 1
	for i, l in enumerate(lines[:-1]):
		l = l.strip()
		l2 = lines[i+1].strip()
		while not os.path.isfile(l2):
			time.sleep(60)
		# submit the job
		basename = os.path.basename(os.path.splitext(l)[0])
		cmd = "/home/kailuyang/scratch/compile/MotionCor2-10-19-2016 --gpu -InMrc {} -OutMrc Corrected_{}.mrc -Patch 6 6 -Iter 10 -Tol 0.5 -Throw 1 -Kv 200 -PixSize 0.935 -FmDose 1.14 -FtBin 2".format(l, basename)
		p3c.ada_gpu(cmd, basename, walltime, gpu, ptile)
	# process the last one
	last = lines[-1].strip()
	size = os.path.getsize(last)
	time.sleep(30)
	size_new = os.path.getsize(last)
	while size_new > size:
		size = size_new
		time.sleep(30)
		size_new = os.path.getsize(last)
	basename = os.path.basename(os.path.splitext(last)[0])
	cmd = "/home/kailuyang/scratch/compile/MotionCor2-10-19-2016 --gpu -InMrc {} -OutMrc ./Corrected_{}.mrc -Patch 6 6 -Iter 10 -Tol 0.5 -Throw 1 -Kv 200 -PixSize 0.935 -FmDose 1.14 -FtBin 2".format(last, basename)
	p3c.ada_gpu(cmd, basename, walltime, gpu, ptile)
		
if __name__ == '__main__':
	main()
