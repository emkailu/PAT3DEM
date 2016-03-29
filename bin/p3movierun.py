#!/usr/bin/env python

import os
import sys
import argparse
import time

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <f.txt>
	Run p3movie.py to process movies listed in f.txt, and the movies will be deleted to save space.
	"""
	
	args_def = {'apix':1.25, 'voltage':200, 'time':200, 'rate':8, 'save':'0 0 0', 'xsuper':7420, 'scale':1, 'delete':1}
	parser = argparse.ArgumentParser()
	parser.add_argument("f", nargs='*', help="specify the txt file used for p3download.py")
	parser.add_argument("-a", "--apix", type=float, help="specify apix, by default {}".format(args_def['apix']))
	parser.add_argument("-v", "--voltage", type=int, help="specify the voltage (kV), by default {}".format(args_def['voltage']))
	parser.add_argument("-t", "--time", type=float, help="specify exposure time per frame in ms, by default {}".format(args_def['time']))
	parser.add_argument("-r", "--rate", type=float, help="specify dose rate in e/pix/s (counting pixel, not superresolution), by default {}. if specified as 0, no filtered sum will be output".format(args_def['rate']))
	parser.add_argument("-s", "--save", type=str, help="save a specified number of aligned frames, by default '{}', which means do not save. e.g., '0 19 4' means the saved movie starts from frame #0, ends at #19, in total (19-0+1)/4 = 5 frames. if 19 >= the real number of frames of the movie, skip".format(args_def['save']))
	parser.add_argument("-x", "--xsuper", type=int, help="specify the x dimension of superresolution images, by default {}".format(args_def['xsuper']))
	parser.add_argument("-sc", "--scale", type=float, help="specify the down scaling factor, by default {}. e.g., 1.2 means counting images will be downscaled by 1.2 times, superresolution 2.4".format(args_def['scale']))
	parser.add_argument("-d", "--delete", type=int, help="delete (!!!) the raw movie (specify as 1), by default {}, which means do not delete".format(args_def['delete']))
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
	walltime, cpu, ptile = 1, 1, 1
	option = "-a {} -v {} -t {} -r {} -s '{}' -x {} -sc {} -d {}".format(args.apix, args.voltage, args.time, args.rate, args.save, args.xsuper, args.scale, args.delete)
	for i, l in enumerate(lines[:-1]):
		l = l.strip()
		l2 = lines[i+1].strip()
		while not os.path.isfile(l2):
			time.sleep(60)
		# submit the job, the option '-d 1' means delete the raw movie!!!
		cmd = "p3movie.py {} {}".format(l, option)
		basename = os.path.basename(os.path.splitext(l)[0])
		p3c.ada(cmd, basename, walltime, cpu, ptile)
	# process the last one
	last = lines[-1].strip()
	size = os.path.getsize(last)
	time.sleep(30)
	size_new = os.path.getsize(last)
	while size_new > size:
		size = size_new
		time.sleep(30)
		size_new = os.path.getsize(last)
	cmd = "p3movie.py {} {}".format(last, option)
	basename = os.path.basename(os.path.splitext(last)[0])
	p3c.ada(cmd, basename, walltime, cpu, ptile)	
		
if __name__ == '__main__':
	main()
