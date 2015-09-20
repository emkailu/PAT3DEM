#!/usr/bin/env python

import os
import sys
import argparse
import pat3dem.cluster as p3c

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <micrograph.mrc>
	output ctffind3 results, skip if micrograph.txt exists
	needs:
	ctffind (v4.0.16, Rohou & Grigorieff, 2015)
	"""
	
	args_def = {'apix':1.25, 'voltage':200, 'defoci':'5000 50000', 'res':'30 5', 'dpsize':5}	
	parser = argparse.ArgumentParser()
	parser.add_argument("image", nargs='*', help="specify micrographs (in mrc format) to be processed")
	parser.add_argument("-a", "--apix", type=float, help="specify apix, by default {}".format(args_def['apix']))
	parser.add_argument("-v", "--voltage", type=int, help="specify the voltage (kV), by default {}".format(args_def['voltage']))
	parser.add_argument("-d", "--defoci", type=str, help="specify a defocus range, by default '{}'".format(args_def['defoci']))
	parser.add_argument("-r", "--res", type=str, help="specify a resolution range, by default '{}'".format(args_def['res']))
	parser.add_argument("-dps", "--dpsize", type=float, help="specify the physical detector pixel size in um, by default '{}'".format(args_def['dpsize']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options"
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# loop over all the input images
	d1, d2 = args.defoci.split()
	r1, r2 = args.res.split()
	xmag = args.dpsize * 10000 / args.apix
	for i in args.image:
		# generate the com file
		out = i[:-4]+'_ctffind3'
		if os.path.isfile(i[:-4]+'.txt'):
			continue
		o_com = out + '.com'
		with open(o_com, 'w') as o_com_w:
			o_com_w.write('{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n'.format('#!/bin/bash', 'ctffind --omp-num-threads 1 --old-school-input << eof', i, i[:-4]+'.ctf', 2, args.voltage, 0.1, xmag, args.dpsize, 512, r1, r2, d1, d2, 500, 100, 'eof'))
		# submit the job
		cmd = "sh {}".format(o_com)
		walltime, cpu, ptile = 1, 1, 1
		p3c.ada(cmd, out, walltime, cpu, ptile)
			
if __name__ == '__main__':
	main()
