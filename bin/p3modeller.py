#!/usr/bin/env python

import os
import sys
import argparse
from modeller import *
from modeller.automodel import *

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <seq>
	Run modeller.
	Needs:
	Modeller (v9.15, Webb & Sali, 2014)
	"""
	
	args_def = {'template':'0', 'chain':'A', 'num':1, 'ali':'0'}	
	parser = argparse.ArgumentParser()
	parser.add_argument("seq", nargs='*', help="Specify a file containing only the target sequence and, optionally, non-sequence lines with '>', if you wish.")
	parser.add_argument("-t", "--template", type=str, help="Specify a pdb file as the template, by default '{}'.".format(args_def['template']))
	parser.add_argument("-c", "--chain", type=str, help="Specify the chain of the template, by default '{}'".format(args_def['chain']))
	parser.add_argument("-n", "--num", type=int, help="Specify how many models you want, by default '{}'".format(args_def['num']))
	parser.add_argument("-a", "--ali", type=str, help="Specify your own alignment file, by default '{}'".format(args_def['ali']))
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
	temp_pdb = args.template
	temp_base = os.path.basename(os.path.splitext(temp_pdb)[0])
	temp_link = temp_base+'.pdb'
	if not os.path.isfile(temp_link):
		os.symlink(temp_pdb, temp_link)
	chain = args.chain
	seq_file = args.seq[0]
	# write a new ali file
	ali_base = os.path.basename(os.path.splitext(seq_file)[0])
	ali = '{}.ali'.format(ali_base)
	with open(seq_file) as ali_read:
		lines = ali_read.readlines()
	seq = ''
	for line in lines:
		if '>' not in line:
			line = line.strip()
			seq += line
	with open(ali, 'w') as ali_write:
		ali_write.write('>P1;{}\n'.format(ali_base))
		ali_write.write('sequence:{}:::::::0.00: 0.00\n'.format(ali_base))
		ali_write.write('{}*\n'.format(seq))
	# sequence alignment with the template
	env = environ()
	aln = alignment(env)
	mdl = model(env, file=temp_base, model_segment=('FIRST:'+chain,'LAST:'+chain))
	aln.append_model(mdl, align_codes=temp_base+chain, atom_files=temp_link)
	aln.append(file=ali, align_codes=ali_base)
	aln.align2d()
	aln_out = '{}_{}.ali'.format(ali_base, temp_base)
	if args.ali == '0':
		aln.write(file=aln_out, alignment_format='PIR')
	else:
		aln_out = args.ali
	# model building
	env = environ()
	a = automodel(env, alnfile=aln_out,
		      knowns=temp_base+chain, sequence=ali_base,
		      assess_methods=(assess.DOPE,
		                      #soap_protein_od.Scorer(),
		                      assess.GA341))
	a.starting_model = 1
	a.ending_model = args.num
	a.make()

if __name__ == '__main__':
	main()
