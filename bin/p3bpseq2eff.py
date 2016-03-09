#!/usr/bin/env python

import os
import sys
import argparse

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <input>
	Convert .bpseq file to .eff file.
	"""
	
	args_def = {'chain':'A','eff':'zz.eff', 'shift':0}	
	parser = argparse.ArgumentParser()
	parser.add_argument("bpseq", nargs='*', help="specify .bpseq files to be processed")
	parser.add_argument("-c", "--chain", type=str, help="specify chain ID, by default {}".format(args_def['chain']))
	parser.add_argument("-e", "--eff", type=str, help="specify an old eff file, by default {}. In this case, a comparison will be made.".format(args_def['eff']))
	parser.add_argument("-s", "--shift", type=int, help="specify the shift, by default {}. E.g., your model start from residue 7, which is save as residue 1 by Assemble, so you specify -s 6".format(args_def['shift']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# read the old eff file, if it exists
	pairs_old = set()
	if os.path.isfile(args.eff):
		with open(args.eff) as e_read:
			lines = e_read.readlines()
		for i, line in enumerate(lines):
			if line == '      base_pair {\n':
				b1 = int(lines[i+1].split()[-1])
				b2 = int(lines[i+2].split()[-1])
				if b1 < b2:
					l = [b1, b2]
				else:
					l = [b2, b1]
				pairs_old.add(tuple(l))
				
	# loop over all the input bpseq
	for bpseq in args.bpseq:
		basename = os.path.basename(os.path.splitext(bpseq)[0])
		with open(bpseq) as b_read:
			lines = b_read.readlines()
		pairs = set()
		for line in lines:
			line = line.split()
			b1 = int(line[0]) + args.shift
			b2 = int(line[2]) + args.shift
			if b1 < b2:
				l = [b1, b2]
			else:
				l = [b2, b1]
			# skip the unpaired residues
			if l[0] == args.shift:
				continue
			pairs.add(tuple(l))
		
		with open(basename+'_bpseq-only.eff', 'w') as e_write:
			for i in pairs.difference(pairs_old):
				e_write.write('      base_pair {\n')
				e_write.write("        base1 = chain '{}' and resid {}\n".format(args.chain, i[0]))
				e_write.write("        base2 = chain '{}' and resid {}\n".format(args.chain, i[1]))
				#e_write.write("        restrain_planarity = True\n")
				#e_write.write("        planarity_sigma = 0.001\n")
				e_write.write('      }\n')
		with open(basename+'_eff-only.eff', 'w') as e_write:
			for i in pairs_old.difference(pairs):
				e_write.write('      base_pair {\n')
				e_write.write("        base1 = chain '{}' and resid {}\n".format(args.chain, i[0]))
				e_write.write("        base2 = chain '{}' and resid {}\n".format(args.chain, i[1]))
				#e_write.write("        restrain_planarity = True\n")
				#e_write.write("        planarity_sigma = 0.001\n")
				e_write.write('      }\n')		
			
if __name__ == '__main__':
	main()
