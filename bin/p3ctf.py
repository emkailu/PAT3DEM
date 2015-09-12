#!/usr/bin/env python

import os
import sys
import argparse
import pat3dem.cluster as p3c

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <micrographs>
	output ctf
	needs:
	ctffind (v4.0.16, Rohou & Grigorieff, 2015)
	"""
	
	parser = argparse.ArgumentParser()
	parser.add_argument("image", nargs='*', help="specify micrographs (in mrc format) to be processed")
	parser.add_argument("-a", "--apix", type=float, help="specify apix, by default 1.25")
	parser.add_argument("-v", "--voltage", type=int, help="specify the voltage (kV), by default 200")
	parser.add_argument("-d", "--defoci", type=str, help="specify a defocus range, by default '5000 50000'")
	args_default = {'apix':1.25, 'voltage':200, 'defoci':'0.5 5'}
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options"
		sys.exit(1)	
	else:
		# get default values
		for i in args_default:
			if args.__dict__[i] == None:
				args.__dict__[i] = args_default[i]
		# loop over all the input images
		d1, d2 = args.defoci.split()
		for i in args.image:
			# generate the com file
			out = i[:-4]+'_ctffind'
			o_com = out + '.com'
			with open(o_com, 'w') as o_com_w:
				o_com_w.write('{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n'.format('#!/bin/bash', 'ctffind << eof', i, i[:-4]+'.ctf', args.apix, args.voltage, 2, 0.1, 512, 30, 5, d1, d2, 500, 100, 'no', 'eof'))
			# submit the job
			cmd = "sh {}".format(o_com)
			title = out
			walltime, cpu, ptile = 1, 1, 1
			p3c.ada(cmd, title, walltime, cpu, ptile)
			
if __name__ == '__main__':
	main()
