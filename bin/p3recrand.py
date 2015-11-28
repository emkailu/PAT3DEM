#!/usr/bin/env python

import os
import sys
import argparse
import pat3dem.star as p3s
import pat3dem.cluster as p3c
import random

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <_data.star>
	Reconstruct from randomly selected particles from _data.star.
	Needs:
	relion (v1.4, Scheres, 2012)
	"""
	
	args_def = {'repeat':1000, 'apix':1.25, 'maxres':6, 'walltime':1}	
	parser = argparse.ArgumentParser()
	parser.add_argument("star", nargs='*', help="specify _data.star")
	parser.add_argument("-r", "--repeat", type=int, help="specify how many times you want to repeat the experiment (reconstruct from random particles), by default {}".format(args_def['repeat']))
	parser.add_argument("-a", "--apix", type=float, help="specify the apix, by default {}".format(args_def['apix']))
	parser.add_argument("-m", "--maxres", type=float, help="specify maximum resolution (in Angstrom) to consider in Fourier space, by default {}".format(args_def['maxres']))
	parser.add_argument("-w", "--walltime", type=int, help="specify the walltime (in hour), by default {}".format(args_def['walltime']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# repeat
	star = args.star[0]
	star_dict = p3s.star_parse(star, 'data_images')
	header = star_dict['data_'] + star_dict['loop_']
	for i in xrange(args.repeat):
		# root name for output
		out = star[:-10] + '_repeat{:05}'.format(i)
		# check if output exists
		if os.path.isfile(out+'.mrc'):
			continue
		# write a new random data.star
		with open(star) as s_read:
			lines = s_read.readlines()[len(header):-1]
			l_len = len(lines)
			new_star = star[:-10] + '_repeat{:05}_data.star'.format(i)
			with open(new_star, 'w') as s_write:
				s_write.write(''.join(header))
				# randomly select for l_len times
				for j in xrange(l_len):
					k = random.randint(0,l_len-1)
					s_write.write(lines[k])
				s_write.write('\n')		
		# write and submit the job
		cmd = "`which relion_reconstruct` --i {} --o {} --angpix {} --maxres {} --ctf true".format(new_star, out+'.mrc', args.apix, args.maxres)
		walltime, cpu, ptile = args.walltime, 1, 1
		p3c.ada(cmd, out, walltime, cpu, ptile)
		
if __name__ == '__main__':
	main()
