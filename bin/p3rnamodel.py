#!/usr/bin/env python

import os
import sys
import argparse
from moderna import *
from operator import itemgetter
from itertools import groupby

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <.alnfasta>
	Build RNA homology models using modeRNA. Only conserved fragments will be output.
	"""
	
	args_def = {'old':'', 'reference':'', 'chain':'A', 'xrna':''}	
	parser = argparse.ArgumentParser()
	parser.add_argument("aln", nargs='*', help="specify an alnfasta containing target sequence first and then reference sequence.")
	parser.add_argument("-o", "--old", type=str, help="specify the pdb file of the old target model, by default '{}'.".format(args_def['old']))
	parser.add_argument("-r", "--reference", type=str, help="specify a pdb file as the reference, by default '{}'. You need to do 'Select, Structure, nucleic acid and Save PDB' in Chimera.".format(args_def['reference']))
	parser.add_argument("-c", "--chain", type=str, help="specify the chain of the reference, by default '{}'".format(args_def['chain']))
	parser.add_argument("-x", "--xrna", type=str, help="specify the a file containing basepairs information in the xrna format, by default '{}'. Note if the StartNucID is wrong, you may use awk (see google document).".format(args_def['xrna']))
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
	seq_t, seq_r = ''.join(seq[0].replace('\r', '\n').split('\n')[1:]), ''.join(seq[1].replace('\r', '\n').split('\n')[1:])
	str_t, str_r = '', ''
	for i in xrange(len(seq_t)):
		if seq_t[i] != '-' or seq_r[i] != '-':
			str_t += seq_t[i].upper()
			str_r += seq_r[i].upper()
	ST, SR = str_t.replace('-', ''), str_r.replace('-', '') # real sequence without dashes
	# write out new alnfasta, which is important for manual modification of the alignment
	aln_n = base + '_new.alnfasta'
	with open(aln_n, 'w') as aln_write:
		aln_write.write(seq[0].split('\n')[0] + '\n')
		aln_write.write(newline(str_t) + '\n')
		aln_write.write(seq[1].split('\n')[0] + '\n')
		aln_write.write(newline(str_r) + '\n')
		print "New alignment has been written in {}, which may need to be modified by hand!".format(aln_n)
	# find conserved fragments
	c_p = {'aln':0, 'un_t':0, 'un_r':0}
	# 'aln' record the number of aligned residues
	# 'un_t' record the number of unaligned residues in target
	# 'un_r' record the number of unaligned residues in ref
	str_t, str_r, c_p = initialize(str_t, str_r, c_p)
	bp = bp_xrna(args.xrna)
	aln_dict = {}
	while len(str_t) * len(str_r) != 0:
		# calculate the length
		frag_t = str_t.split('-')[0]
		frag_r = str_r.split('-')[0]
		length = min(len(frag_t), len(frag_r))
		# check if this length in the basepaired region
		# check the starting point, which should not start with "aligned" loop (because it's not really "aligned")
		aln_loop = 0 # length of starting "aligned" loop
		while c_p['aln'] + c_p['un_t'] + aln_loop + 1 not in bp and aln_loop < length:
			aln_loop += 1
		start_t = c_p['aln'] + c_p['un_t'] + aln_loop + 1# start num of target, 1 means the first
		start_r = c_p['aln'] + c_p['un_r'] + aln_loop + 1
		# check the end point, which should not start with "aligned" loop either
		aln_loop_end = 0
		while c_p['aln'] + c_p['un_t'] + length - aln_loop_end not in bp and aln_loop_end < length - aln_loop:
			aln_loop_end += 1
		end_t = c_p['aln'] + c_p['un_t'] + length - aln_loop_end # end num of target
		end_r = c_p['aln'] + c_p['un_r'] + length - aln_loop_end
		if start_t < end_t:
			aln_dict[(start_t, end_t)] = (start_r, end_r) # store the aln in aln_dict
		c_p['aln'] += length
		str_t = str_t[length:]
		str_r = str_r[length:]
		str_t, str_r, c_p = initialize(str_t, str_r, c_p)
	# moderna
	m = load_model(args.reference, args.chain)
	remove_all_modifications(m)
	base_pdb = os.path.basename(os.path.splitext(args.reference)[0])
	rmmd = base_pdb + '_rmmd.pdb'
	m.write_pdb_file(rmmd)
	print "The reference has been written in {} after removing modifications.".format(rmmd)
	SR_brk = str(get_sequence(m)) # the reference may be broken, which is shown as an underscore.
	# loop through all the fragments
	merge = create_model()
	for t, r in aln_dict.iteritems():
		if SR[r[0]-1:r[1]] in SR_brk:# only if the ref is not broken here
			base_t = '{}_{}-{}'.format(base,t[0],t[1])
			base_r = '{}_{}-{}'.format(base_pdb,r[0],r[1])
			t_pdb = base_t + '.pdb'
			r_pdb = base_r + '.pdb'
			aln_f = '{}_{}-{}.alnfasta'.format(base_t,r[0],r[1])
			m_r = create_model()
			copy_some_residues(m[str(r[0]):str(r[1])],m_r) # moderna 1 means the first
			m_r.write_pdb_file(r_pdb)
			print "The fragmented reference has been written in {}.".format(r_pdb)
			with open(aln_f, 'w') as f_w:
				f_w.write(seq[0].split('\n')[0] + '\n')
				f_w.write(newline(ST[t[0]-1:t[1]]) + '\n')
				f_w.write(seq[1].split('\n')[0] + '\n')
				f_w.write(newline(SR[r[0]-1:r[1]]) + '\n')
				print "Fragmented alignment has been written in {}!".format(aln_f)
			r= load_template(r_pdb)
			a = load_alignment(aln_f)
			m_t = create_model(r, a)
			renumber_chain(m_t,str(t[0]))
			m_t.write_pdb_file(t_pdb)
			print "Fragmented homology model has been written in {}!".format(t_pdb)
			print
			m_t = load_template(t_pdb)
			copy_some_residues(m_t,merge)
		merge.write_pdb_file(base + '_merge.pdb')
	# if you specified the old model
	if args.old != '':
		m_o = load_model(args.old)
		old = os.path.basename(os.path.splitext(args.old)[0])
		l_list = sorted(list(set(xrange(1,3139)) - set(bp)))
		for k, g in groupby(enumerate(l_list), lambda (i,x):i-x):
			r = map(itemgetter(1), g)
			r = [str(r[0]-1), str(r[-1]+1)]
			loop = create_model()
			copy_some_residues(m_o[r[0]:r[1]],loop)
			
			l_pdb = '{}_{}-{}.pdb'.format(old,r[0],r[1])
			loop.write_pdb_file(l_pdb)
			#f = create_fragment('loop.pdb', merge[r[0]], merge[r[1]])
			#insert_fragment(merge, f)
		#merge.write_pdb_file(base + '_merge2.pdb')

def newline(string, every=10):
	return '\n'.join(string[i:i+every] for i in xrange(0, len(string), every))

def bp_xrna(xrna):
	# get the numbering of basepaired residues from xrna file. 1 means the first.
	bp = []
	with open(xrna) as x:
		for line in x:
			if line[:10] == '<BasePairs':
				l = line.split("'")
				start, length, end = int(l[1]), int(l[3]), int(l[5])
				bp += range(start, start+length) + range(end-length+1, end+1)
	return bp
	
def initialize(str_t, str_r, c_p):
	# make sure the strings don't start with dashes
	if len(str_t) * len(str_r) != 0:
		while str_t[0] == '-' or str_r[0] == '-':
			if str_t[0] != '-':
				c_p['un_t'] += 1
			if str_r[0] != '-':
				c_p['un_r'] += 1
			str_t = str_t[1:]
			str_r = str_r[1:]
			if len(str_t) * len(str_r) == 0:
				return str_t, str_r, c_p
	return str_t, str_r, c_p
				
if __name__ == '__main__':
	main()
