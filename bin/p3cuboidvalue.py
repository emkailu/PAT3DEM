#!/usr/bin/env python

import os
import sys
import argparse
import pat3dem.main as p3m

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <images>
	Output the values of voxels within a coordinate range, 'x1 x2 y1 y2 z1 z2'
	Needs:
	EMAN2 (v2.11, Tang et al., 2007)
	"""
	
	args_def = {'coord':'-1 '*6}	
	parser = argparse.ArgumentParser()
	parser.add_argument("image", nargs='*', help="specify images to be processed")
	parser.add_argument("-c", "--coord", type=str, help="specify a coordinate range, 'x1 x2 y1 y2 z1 z2', by default '{}', which means do nothing".format(args_def['coord']))
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
	if args.coord == '-1 '*6:
		sys.exit("What's the point if you don't specify coordinates?")
	x1, x2, y1, y2, z1, z2 = p3m.get_coord(args.coord)
	# loop over input images
	i_dict = {}
	for i in args.image:
		# get values
		i_dict[i] = p3m.get_value(i, args.coord)
		# plot histogram
		num = i_dict[i].values()
		p3m.plot_hist(num, i[:-4]+'_{}-{}_{}-{}_{}-{}.png'.format(x1, x2, y1, y2, z1, z2))
		
if __name__ == '__main__':
	main()
