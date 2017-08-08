#!/usr/bin/env python

import os
import sys
import argparse

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <*.alnfasta>
	Convert alnfasta file to _ref.params to be used in phenix.
	"""
	
	args_def = {'ref':'0', 'chain_ref':'A', 'chain_target':'A'}	
	parser = argparse.ArgumentParser()
	parser.add_argument("aln", nargs='*', help="specify an alnfasta containing target sequence first and then reference sequence.")
	parser.add_argument("-r", "--ref", type=str, help="specify a pdb file as the reference, by default '{}'.".format(args_def['ref']))
	parser.add_argument("-cr", "--chain_ref", type=str, help="specify the chain of the reference, by default '{}'".format(args_def['chain_ref']))
	parser.add_argument("-ct", "--chain_target", type=str, help="specify the chain of the target, by default '{}'".format(args_def['chain_target']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# first remove unnecessary dashes, and capitalize
	aln = args.aln[0]
	base = os.path.basename(os.path.splitext(aln)[0])
	seq = []
	i = -1
	with open(aln) as aln_read:
		for line in aln_read:
			if '>' in line:
				seq += ['']
				i += 1
			seq[i] += line
	seq_target, seq_ref = ''.join(seq[0].replace('\r', '\n').split('\n')[1:]), ''.join(seq[1].replace('\r', '\n').split('\n')[1:])
	str_target, str_ref = '', ''
	for i in xrange(len(seq_target)):
		if seq_target[i] != '-' or seq_ref[i] != '-':
			str_target += seq_target[i].upper()
			str_ref += seq_ref[i].upper()
	# write out new alnfasta, which is important for manual modification of the alignment
	aln_n = base + '_new.alnfasta'
	with open(aln_n, 'w') as aln_write:
		aln_write.write(seq[0].split('\n')[0] + '\n')
		aln_write.write(str_target + '\n')
		aln_write.write(seq[1].split('\n')[0] + '\n')
		aln_write.write(str_ref + '\n')
	# write .ref.params
	with open(base+'_ref.params', 'w') as ref_write:
		ref_write.write('refinement.reference_model.file = {}\n'.format(args.ref))
		# 'common' record the number of aligned residues
		# 'd_target' record the number of unaligned residues in target
		# 'd_ref' record the number of unaligned residues in ref
		c_p = {'common':0, 'd_target':0, 'd_ref':0}
		str_target, str_ref, c_p = initialize(str_target, str_ref, c_p)
		while len(str_target) * len(str_ref) != 0:
			frag_target = str_target.split('-')[0]
			frag_ref = str_ref.split('-')[0]
			span = min(len(frag_target), len(frag_ref))
			ref_write.write('refinement.reference_model.reference_group {\n')
			ref_write.write('    reference = chain {} and resseq {}:{}\n'.format(args.chain_ref, c_p['common'] + c_p['d_ref'] + 1, c_p['common'] + c_p['d_ref'] + span))
			ref_write.write('    selection = chain {} and resseq {}:{}\n'.format(args.chain_target, c_p['common'] + c_p['d_target'] + 1, c_p['common'] + c_p['d_target'] + span))
			ref_write.write('    file_name = {}\n'.format(args.ref))
			ref_write.write('   }\n')
			c_p['common'] += span
			str_target = str_target[span:]
			str_ref = str_ref[span:]
			str_target, str_ref, c_p = initialize(str_target, str_ref, c_p)
			
def initialize(str_target, str_ref, c_p):
	if len(str_target) * len(str_ref) != 0:
		while str_target[0] == '-' or str_ref[0] == '-':
			if str_target[0] != '-':
				c_p['d_target'] += 1
			if str_ref[0] != '-':
				c_p['d_ref'] += 1
			str_target = str_target[1:]
			str_ref = str_ref[1:]
			if len(str_target) * len(str_ref) == 0:
				sys.exit(1)
	return str_target, str_ref, c_p
				
if __name__ == '__main__':
	main()
