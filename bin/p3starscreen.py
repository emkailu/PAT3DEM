#!/usr/bin/env python

import os
import sys
import argparse
import pat3dem.star as p3s

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <a star file>
	Write two new star files after screening by an item in the star file.
	"""
	
	args_def = {'screen':'0'}	
	parser = argparse.ArgumentParser()
	parser.add_argument("star", nargs='*', help="specify a star file to be screened")
	parser.add_argument("-s", "--screen", type=str, help="specify the item, by which the star file will be screened, by default {} (no screening). e.g., 'OriginX 5.2'".format(args_def['screen']))
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
	if args.screen == '0':
		sys.exit("You don't want any screening.")
	# Get the screening criterium
	sc = args.screen.split()
	# Get the star file
	star = args.star[0]
	basename = os.path.basename(os.path.splitext(star)[0])
	# Name the output files
	screened1 = '{}_screened_{}-gt-{}.star'.format(basename, sc[0], sc[-1])
	write_screen1 = open(screened1, 'w')
	screened2 = '{}_screened_{}-le-{}.star'.format(basename, sc[0], sc[-1])
	write_screen2 = open(screened2, 'w')
	star_dict = p3s.star_parse(star, 'data_')
	# get the sc number
	scn = star_dict['_rln'+sc[0]]
	# write header
	header = star_dict['data_'] + star_dict['loop_']
	write_screen1.write(''.join(header))
	write_screen2.write(''.join(header))
	header_len = len(header)
	with open(star) as read_star:
		lines = read_star.readlines()[header_len:-1]
	for line in lines:
		if float(line.split()[scn]) > float(sc[-1]):
			write_screen1.write(line)
		else:
			write_screen2.write(line)
	write_screen1.write(' \n')
	write_screen1.close()
	write_screen2.write(' \n')
	write_screen2.close()
	print 'The screened star files have been written in {} and {}!'.format(screened1, screened2)

if __name__ == '__main__':
	main()
