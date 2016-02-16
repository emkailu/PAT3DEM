#!/usr/bin/env python

import os
import sys
import argparse

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <input>
	Convert .bpseq file to .eff file.
	"""
	
	args_def = {'chain':'A'}	
	parser = argparse.ArgumentParser()
	parser.add_argument("bpseq", nargs='*', help="specify .bpseq files to be processed")
	parser.add_argument("-c", "--chain", type=str, help="specify chain ID, by default {}".format(args_def['chain']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# loop over all the input bpseq
	for bpseq in args.bpseq:
		basename = os.path.basename(os.path.splitext(bpseq)[0])
		with open(bpseq) as b_read:
			lines = b_read.readlines()
		pairs = set()
		for line in lines:
			line = line.split()
			b1 = int(line[0])
			b2 = int(line[2])
			if b1 < b2:
				l = [b1, b2]
			else:
				l = [b2, b1]
			# skip the unpaired residues
			if l[0] == 0:
				continue
			pairs.add(tuple(l))
		with open(basename+'.eff', 'w') as e_write:
			for i in pairs:
				e_write.write('      base_pair }\n')
				e_write.write("        base1 = chain '{}' and resid {}\n".format(args.chain, i[0]))
				e_write.write("        base2 = chain '{}' and resid {}\n".format(args.chain, i[1]))
				e_write.write('      }\n')
			
				
if __name__ == '__main__':
	main()
