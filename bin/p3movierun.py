#!/usr/bin/env python

import os
import sys
import argparse
import time
import pat3dem.cluster as p3c

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <f.txt>
	run p3movie.py after p3download.py
	"""
	
	args_def = {'apix':1.25, 'voltage':200, 'time':200, 'rate':4, 'save':'0 0 0', 'save2':'0 0 0', 'xsuper':7420}
	parser = argparse.ArgumentParser()
	parser.add_argument("f", nargs='*', help="specify the txt file used for p3download.py")
	parser.add_argument("-a", "--apix", type=float, help="specify apix, by default {}".format(args_def['apix']))
	parser.add_argument("-v", "--voltage", type=int, help="specify the voltage (kV), by default {}".format(args_def['voltage']))
	parser.add_argument("-t", "--time", type=float, help="specify exposure time per frame in ms, by default {}".format(args_def['time']))
	parser.add_argument("-r", "--rate", type=float, help="specify dose rate in e/pix/s (counting pixel, not superresolution), by default {}".format(args_def['rate']))
	parser.add_argument("-s", "--save", type=str, help="save a specified number of aligned frames, by default {}, which means do not save. e.g., '0 19 4' means the saved movie starts from frame #0, ends at #19, in total (19-0+1)/4 = 5 frames".format(args_def['save']))
	parser.add_argument("-s2", "--save2", type=str, help="save a second specified number of aligned frames, by default {}, which means do not save. e.g., '0 31 4' means the saved movie starts from frame #0, ends at #19, in total (31-0+1)/4 = 8 frames".format(args_def['save2']))
	parser.add_argument("-x", "--xsuper", type=int, help="specify the x dimension of superresolution images, by default {}".format(args_def['xsuper']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options"
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# get the local file list based on f.txt
	f = args.f[0]
	f2 = f + '.txt'
	with open(f) as f_r:
		lines = f_r.readlines()
	with open(f2, 'w') as f2_w:
		for i in lines:
			j = './' + i.replace('\\','/').split('/')[-1]
			f2_w.write(j)
	with open(f2) as f2_r:
		lines = f2_r.readlines()
	# run line #i if line #(i+1) exists, the last line will be ignored
	for i, l in enumerate(lines[:-1]):
		l = l.strip()
		l2 = lines[i+1].strip()
		while not os.path.isfile(l2):
			time.sleep(60)
		# submit the job, the option '-d 1' means delete the raw movie!!!
		basename = os.path.basename(os.path.splitext(l)[0])
		cmd = "p3movie.py {} -a {} -v {} -t {} -r {} -s '{}' -s2 '{}' -x {} -d 1".format(l, args.apix, args.voltage, args.time, args.rate, args.save, args.save2, args.xsuper)
		walltime, cpu, ptile = 1, 1, 1
		p3c.ada(cmd, basename, walltime, cpu, ptile)
				
if __name__ == '__main__':
	main()
