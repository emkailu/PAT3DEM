#!/usr/bin/env python

import os
import sys
import argparse
import pat3dem.star as p3s

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <a star file>
	Write two star files after screening by an item and a cutoff in the star file.
	Write one star file after screening by a file containing blacklist/whitelist (either keyword or item).
	"""
	
	args_def = {'screen':'0', 'cutoff':'00', 'sfile':'0', 'white':0}	
	parser = argparse.ArgumentParser()
	parser.add_argument("star", nargs='*', help="specify a star file to be screened")
	parser.add_argument("-s", "--screen", type=str, help="specify the item, by which the star file will be screened, by default {} (no screening). e.g., 'OriginX'".format(args_def['screen']))
	parser.add_argument("-c", "--cutoff", type=str, help="specify the cutoff, by default '{}' (-s and -sf will be combined).".format(args_def['cutoff']))
	parser.add_argument("-sf", "--sfile", type=str, help="specify a file containing a keyword each line, by default '{}' (no screening). e.g., 'f.txt'".format(args_def['sfile']))
	parser.add_argument("-w", "--white", type=int, help="specify as 1 if you provide a whitelist in -sf".format(args_def['white']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options"
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# preprocess -sf
	if args.sfile != '0':
		lines_sf = open(args.sfile).readlines()
		lines_sfile = []
		for line in lines_sf:
			line = line.strip()
			if line != '':
				lines_sfile += [line]
	# get the star file
	star = args.star[0]
	basename = os.path.basename(os.path.splitext(star)[0])
	star_dict = p3s.star_parse(star, 'data_')
	header = star_dict['data_'] + star_dict['loop_']
	header_len = len(header)
	with open(star) as read_star:
		lines = read_star.readlines()[header_len:-1]
	if args.screen != '0':		
		# get the sc number
		scn = star_dict['_rln'+args.screen]	
		if args.cutoff != '00':
			# Name the output files
			screened1 = '{}_screened_{}-gt-{}.star'.format(basename, args.screen, args.cutoff)
			screened2 = '{}_screened_{}-le-{}.star'.format(basename, args.screen, args.cutoff)
			write_screen1 = open(screened1, 'w')
			write_screen1.write(''.join(header))
			write_screen2 = open(screened2, 'w')
			write_screen2.write(''.join(header))
			for line in lines:
				if float(line.split()[scn]) > float(args.cutoff):
					write_screen1.write(line)
				else:
					write_screen2.write(line)
			write_screen1.write(' \n')
			write_screen1.close()
			write_screen2.write(' \n')
			write_screen2.close()
			print 'The screened star files have been written in {} and {}!'.format(screened1, screened2)
		elif args.sfile != '0':		
			with open('{}_screened.star'.format(basename), 'w') as write_screen:
				write_screen.write(''.join(header))
				if args.white == 0:
					for line in lines:
						key = line.split()[scn]
						if key not in lines_sfile:
							print 'Include {}.'.format(key)
							write_screen.write(line)
				else:
					for line in lines:
						key = line.split()[scn]
						if key in lines_sfile:
							print 'Include {}.'.format(key)
							write_screen.write(line)
				write_screen.write(' \n')
	elif args.sfile != '0':
		with open('{}_screened.star'.format(basename), 'w') as write_screen:
			write_screen.write(''.join(header))
			if args.white == 0:
				for line in lines:
					skip = 0
					for key in lines_sfile:
						if key in line:
							skip = 1
							print 'Skip {}.'.format(key)
							break
					if skip == 0:
						write_screen.write(line)
			else:
				for line in lines:
					for key in lines_sfile:
						if key in line:
							print 'Include {}.'.format(key)
							write_screen.write(line)
							break
			write_screen.write(' \n')
						
if __name__ == '__main__':
	main()
