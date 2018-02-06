#!/usr/bin/env python

import os
import sys
import argparse
import pat3dem.star as p3s
import math

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <coord star files>
	Output the coord star files after deleting duplicate particles
	"""
	
	args_def = {'mindis':150}	
	parser = argparse.ArgumentParser()
	parser.add_argument("star", nargs='*', help="specify coord star files to be processed")
	parser.add_argument("-m", "--mindis", type=float, help="specify the minimum distance between particles in pixels, by default {}".format(args_def['mindis']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# loop over all input files		
	for star in args.star:
		star_dict = p3s.star_parse(star, 'data_')
		header = star_dict['data_']+star_dict['loop_']
		header_len = len(header)
		basename = os.path.basename(os.path.splitext(star)[0])
		with open(star) as s_read:
			lines = s_read.readlines()[header_len:-1]
		#
		with open(basename+'_checked.star', 'w') as s_w:
			s_w.write(''.join(header))
			# use list of list to store x and y
			xy = []
			for line in lines:
				good = 1
				line = line.split()
				# get coord
				x, y = float(line[star_dict['_rlnCoordinateX']]), float(line[star_dict['_rlnCoordinateY']])
				for i in xy:
					dis = math.sqrt((x - i[0])**2 + (y - i[1])**2)
					if dis < args.mindis:
						print 'Distance between ({},{}) and {} is {}. Discard.'.format(x,y,i,dis)
						good = 0
						break
				if good == 1:
					s_w.write('{:>12} '.format(x) + '{:>12} \n'.format(y))
					xy.append((x,y))
			s_w.write('\n')
			
if __name__ == '__main__':
	main()
