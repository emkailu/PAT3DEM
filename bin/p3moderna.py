#!/usr/bin/env python

import os
import sys
import argparse
from moderna import *

def replace(s):
	return s.replace('-', '')

def brk(str0, str1, str_t):
	str0r, str1r = replace(str0), replace(str1)
	str_t = str_t.split('_')
	# in str1r, find the start and end of each fragment of str_t
	index_start = []
	index_end = []
	for i, frag in enumerate(str_t):
		pos = str1r.find(frag)
		if pos == -1:
			sys.exit('Cannot find\n{}\nin\n{}\n!'.format(frag, str1r))
		index_start += [pos]
		index_end += [pos + len(frag) - 1]
	# find the relationship between numberings of str1 and str1r
	rel = {}
	j = 0
	for i, na in enumerate(str1):
		if na != '-':
			rel[j] = i
			j += 1
	# add '_'
	str0n = ''
	str1n = ''
	for i, pos in enumerate(index_start):
		start, end = rel[index_start[i]], rel[index_end[i]]+1
		str0n += str0[start:end] + '_'
		str1n += str1[start:end] + '_'
	return str0n, str1n

def dgap(str0, str1, gap):
	frags = []
	for i in str1.split('-'*gap):
		if i != '':
			i = i.strip('-')
			frags += [i]
	# in str1, find the start and end of each frag
	index_start = []
	index_end = []
	for i, frag in enumerate(frags):
		pos = str1.find(frag)
		if pos == -1:
			sys.exit('Cannot find\n{}\nin\n{}\n!'.format(frag, frags))
		index_start += [pos]
		index_end += [pos + len(frag) - 1]
	# add '_'
	str0n = ''
	str1n = ''
	for i, pos in enumerate(index_start):
		start, end = index_start[i], index_end[i]+1
		str0n += str0[start:end] + '_'
		str1n += str1[start:end] + '_'
	return str0n.strip('_'), str1n.strip('_')

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <alnfasta>
	Run modeRNA without manual preparation.
	Needs:
	ModeRNA (v1.7.1, Rother et al., 2011)
	"""
	
	args_def = {'template':'0', 'chain':'A', 'gap':10}	
	parser = argparse.ArgumentParser()
	parser.add_argument("aln", nargs='*', help="specify an alnfasta containing target sequence first and then template sequence.")
	parser.add_argument("-t", "--template", type=str, help="specify a pdb file as the template, by default '{}'. You need to do 'Select, Structure, nucleic acid and Save PDB' in Chimera.".format(args_def['template']))
	parser.add_argument("-c", "--chain", type=str, help="specify the chain of the template, by default '{}'".format(args_def['chain']))
	parser.add_argument("-g", "--gap", type=int, help="specify the maximum gap you want, by default {}".format(args_def['gap']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# first remove unnecessary dashes and capitalize
	aln = args.aln[0]
	base = os.path.basename(os.path.splitext(aln)[0])
	with open(aln) as aln_read:
		lines = aln_read.readlines()
	seq = []
	i = -1
	for line in lines:
		if '>' in line:
			seq += ['']
			i += 1
		seq[i] += line
	seq0 = ''.join(seq[0].split('\n')[1:])
	seq1 = ''.join(seq[1].split('\n')[1:])
	str0 = ''
	str1 = ''
	for i in xrange(len(seq0)):
		if seq0[i] != '-' or seq1[i] != '-':
			str0 += seq0[i].upper()
			str1 += seq1[i].upper()
	# then delete sequences that are absent in the template pdb or longer than args.gap
	m = load_model(args.template, args.chain)
	remove_all_modifications(m)
	base_pdb = os.path.basename(os.path.splitext(args.template)[0])
	rmmd = base_pdb + '_rmmd.pdb'
	m.write_pdb_file(rmmd)
	str_t = str(get_sequence(m))
	# replace broken part with '_'
	str0, str1 = brk(str0, str1, str_t)
	# delete gaps
	str0, str1 = dgap(str0, str1, args.gap)
	aln_n = base + '_new.alnfasta'
	with open(aln_n, 'w') as aln_write:
		aln_write.write(seq[0].split('\n')[0] + '\n')
		aln_write.write(str0 + '\n')
		aln_write.write(seq[1].split('\n')[0] + '\n')
		aln_write.write(str1 + '\n')
	# run moderna
	t = load_template(rmmd, args.chain)
	a = load_alignment(aln_n)
	m = create_model(t, a)
	m.write_pdb_file(base_pdb + '_moderna.pdb')
			
if __name__ == '__main__':
	main()
