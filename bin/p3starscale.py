#!/usr/bin/env python

import os
import sys
import argparse
import pat3dem.star as p3s

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <a star file>
	Write a new star file after scaling.
	"""
	
	args_def = {'scale':0.5}	
	parser = argparse.ArgumentParser()
	parser.add_argument("star", nargs='*', help="specify a star file to be processed")
	parser.add_argument("-s", "--scale", type=float, help="specify the down scaling factor, by default {}. e.g., 2 means downscaled by 2 times".format(args_def['scale']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options"
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	#
	star = args.star[0]
	basename = os.path.basename(os.path.splitext(star)[0])
	scaled = '{}_scaled_{}.star'.format(basename, args.scale)
	write_scale = open(scaled, 'w')
	star_dict = p3s.star_parse(star, 'data_')
	# get _rlnDetectorPixelSize, _rlnOriginX, _rlnOriginY
	dps, ox, oy = star_dict['_rlnDetectorPixelSize'], star_dict['_rlnOriginX'], star_dict['_rlnOriginY']
	# write header
	header = star_dict['data_'] + star_dict['loop_']
	write_scale.write(''.join(header))
	header_len = len(header)
	with open(star) as read_star:
		lines = read_star.readlines()[header_len:-1]
	for line in lines:
		line = line.split()
		line[dps] = str(float(line[dps]) * args.scale)
		line[ox] = str(float(line[ox]) / args.scale)
		line[oy] = str(float(line[oy]) / args.scale)
		write_scale.write(' '.join(line) + '\n')
	write_scale.write(' \n')
	write_scale.close()
	print 'The scaled star file has been written in {}!'.format(scaled)

if __name__ == '__main__':
	main()
