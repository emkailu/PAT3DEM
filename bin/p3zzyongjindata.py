#!/usr/bin/env python

import os
import sys
import argparse

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <input>
	Process yongjin's data.
	"""
	
	args_def = {'cutoff':10, 'va':'', 'vab':''}	
	parser = argparse.ArgumentParser()
	parser.add_argument("input", nargs='*', help="specify input to be processed")
	parser.add_argument("-c", "--cutoff", type=int, help="specify cutoff*100, by default {}".format(args_def['cutoff']))
	parser.add_argument("-va", "--va", type=str, help="specify va.csv, by default {}".format(args_def['va']))
	parser.add_argument("-vab", "--vab", type=str, help="specify vab.csv, by default {}".format(args_def['vab']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# get va into va_dict
	with open(args.va) as va:
		lines = va.readlines()
	va_dict = {}
	for line in lines[1:]:
		line = line.split(',')
		va_dict[line[0]] = float(line[1])
	# read vab	
	with open(args.vab) as vab:
		lines = vab.readlines()
	basename = os.path.basename(os.path.splitext(args.vab)[0])
	cut = args.cutoff/100.0
	out = '{}_cutoff{}.csv'.format(basename,cut)
	# case1
	with open(out,'w') as vab_new:
		for line in lines[1:]:
			l = line.split(',')
			if va_dict[l[0]] >= cut and va_dict[l[1]] >= cut:
				vab_new.write(line)
	# case2
	with open(out) as vab_new:
		char = vab_new.read()
	with open(out,'a') as vab_new:
		for line in lines[1:]:
			l = line.split(',')
			if va_dict[l[0]] > va_dict[l[1]]:
				l0 = l[0]
				l1 = l[1]
			else:
				l0 = l[1]
				l1 = l[0]
			if va_dict[l0] >= cut and va_dict[l1] < cut and l0 not in char:
				vab_new.write('{},{},self\n'.format(l0,l0))
			
if __name__ == '__main__':
	main()
