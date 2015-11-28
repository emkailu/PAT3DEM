#!/usr/bin/env python

import os
import sys
import argparse
import time
import pat3dem.cluster as p3c

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <f.txt>
	Run p3movie.py to process movies listed in f.txt (except the last one), and the movies will be deleted to save space.
	"""
	
	args_def = {'apix':1.25, 'save':'0 0 0', 'save2':'0 0 0', 'xsuper':7420, 'delete':1}
	parser = argparse.ArgumentParser()
	parser.add_argument("f", nargs='*', help="specify the txt file used for p3download.py")
	parser.add_argument("-a", "--apix", type=float, help="specify apix, by default {}".format(args_def['apix']))
	parser.add_argument("-s", "--save", type=str, help="save a specified number of aligned frames, by default {}, which means do not save. e.g., '2 19 2' means the saved movie starts from frame #2, ends at #19, in total (19-2+1)/2 = 9 frames. if 19 >= the real number of frames of the movie, skip".format(args_def['save']))
	parser.add_argument("-s2", "--save2", type=str, help="save a second specified number of aligned frames, by default {}, which means do not save. e.g., '2 31 2' means the saved movie starts from frame #2, ends at #31, in total (31-2+1)/2 = 15 frames. if 31 >= the real number of frames of the movie, skip".format(args_def['save2']))
	parser.add_argument("-x", "--xsuper", type=int, help="specify the x dimension of superresolution images, by default {}".format(args_def['xsuper']))
	parser.add_argument("-d", "--delete", type=int, help="delete (!!!) the raw movie (specify as 1), by default {}".format(args_def['delete']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
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
	for i, l in enumerate(lines[:-1]):
		l = l.strip()
		l2 = lines[i+1].strip()
		while not os.path.isfile(l2):
			time.sleep(60)
		# submit the job, the option '-d 1' means delete the raw movie!!!
		basename = os.path.basename(os.path.splitext(l)[0])
		cmd = "p3movie.py {} -a {} -s '{}' -s2 '{}' -x {} -d {}".format(l, args.apix, args.save, args.save2, args.xsuper, args.delete)
		walltime, cpu, ptile = 1, 1, 1
		p3c.ada(cmd, basename, walltime, cpu, ptile)
				
if __name__ == '__main__':
	main()
