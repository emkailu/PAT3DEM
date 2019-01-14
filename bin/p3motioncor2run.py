#!/usr/bin/env python

import os
import sys
import argparse
import time

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <f.txt>
	Run p3motoincor2.py to process movies listed in f.txt.
	"""
	
	args_def = {'apix':1.315, 'apixr':0.6575, 'bin':1, 'patch':5, 'voltage':300, 'time':200, 'rate':7, 'target':5, 'tilt':'0 0', 'gainref':'', 'path':'../rawmovies/'}
	parser = argparse.ArgumentParser()
	parser.add_argument("f", nargs='*', help="specify the txt file used for p3download.py")
	parser.add_argument("-a", "--apix", type=float, help="specify counting apix, by default {}".format(args_def['apix']))
	parser.add_argument("-ar", "--apixr", type=float, help="specify real apix of input movie, by default {}".format(args_def['apixr']))
	parser.add_argument("-b", "--bin", type=float, help="specify binning factor, by default {}".format(args_def['bin']))
	parser.add_argument("-p", "--patch", type=int, help="specify the patch, by default {}".format(args_def['patch']))
	parser.add_argument("-v", "--voltage", type=int, help="specify the voltage (kV), by default {}".format(args_def['voltage']))
	parser.add_argument("-t", "--time", type=float, help="specify exposure time per frame in ms, by default {}".format(args_def['time']))
	parser.add_argument("-r", "--rate", type=float, help="specify dose rate in e/pix/s (counting pixel, not superresolution), by default {}".format(args_def['rate']))
	parser.add_argument("-ta", "--target", type=float, help="specify the target resolution, by default {}".format(args_def['target']))
	parser.add_argument("-ti", "--tilt", type=str, help="specify the tilt, by default {}".format(args_def['tilt']))
	parser.add_argument("-g", "--gainref", type=str, help="specify the gainref option, by default {}. e.g., '-Gain ../14sep05c_raw_196/norm-amibox05-0.mrc -RotGain 0 -FlipGain 1'".format(args_def['gainref']))
	parser.add_argument("-pa", "--path", type=str, help="specify the path of raw movies, by default {}".format(args_def['path']))
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
	walltime, gpu, ptile = 10, 1, 1
	option = "-a {} -ar {} -b {} -p {} -v {} -t {} -r {} -ta {} -ti '{}' -g '{}'".format(args.apix, args.apixr, args.bin, args.patch, args.voltage, args.time, args.rate, args.target, args.tilt, args.gainref)
	for i, l in enumerate(lines[:-1]):
		l = l.strip()
		l2 = lines[i+1].strip()
		while not os.path.isfile(args.path+l2):
			time.sleep(60)
		# submit the job
		cmd = "p3motioncor2.py {}{} {}".format(args.path, l, option)
		basename = os.path.basename(os.path.splitext(l)[0])
		p3c.terra(cmd, basename, walltime, gpu, ptile)
	# process the last one
	last = lines[-1].strip()
	size = os.path.getsize(last)
	time.sleep(30)
	size_new = os.path.getsize(last)
	while size_new > size:
		size = size_new
		time.sleep(30)
		size_new = os.path.getsize(last)
	cmd = "p3motioncor2.py {}{} {}".format(args.path, last, option)
	basename = os.path.basename(os.path.splitext(last)[0])
	p3c.terra(cmd, basename, walltime, cpu, ptile)		
			
if __name__ == '__main__':
	main()
