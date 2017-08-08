#!/usr/bin/env python

import os
import sys
import argparse
from Bio.PDB import *
from operator import itemgetter
from itertools import groupby

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <pdb>
	Process pdb.
	"""
	
	args_def = {'chain':'A', 'lenloop':'3', 'xrna':''}	
	parser = argparse.ArgumentParser()
	parser.add_argument("pdb", nargs='*', help="specify pdb to be processed")
	parser.add_argument("-c", "--chain", type=str, help="specify the chain, by default '{}'".format(args_def['chain']))
	parser.add_argument("-l", "--lenloop", type=int, help="specify the minimum length of a loop (shorter loops will be grouped to the adjacent helix), by default '{}'".format(args_def['lenloop']))
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
	# 
	with open('region.level1.data', 'w') as region:
		bp = bp_xrna(args.xrna)
		parser=PDBParser()
		basename = os.path.basename(os.path.splitext(args.pdb[0])[0])
		s=parser.get_structure(basename, args.pdb[0])
		unp = [] #unpaired
		for residue in s.get_residues():
			rdid = residue.get_full_id()
			seqid = rdid[3][1]	
			if seqid not in bp:
				unp += [seqid]
		loops = []
		loops_short = []
		for k, g in groupby(enumerate(unp), lambda (i,x):i-x):
			loops += [map(itemgetter(1), g)]	
		for loop in loops:
			if len(loop) < args.lenloop:
				loops_short += [loop]
				continue
			region.write(r'~region[\element_top_type{residue}'+'\n')
			region.write(r'        \dependency_type{independent}'+'\n')
			region.write(r'        \nres{'+str(len(loop))+'}\n')
			res = []
			for i in loop:
				res += ['{}:{}'.format(args.chain,i)]
			region.write(r'        \residues{'+','.join(res)+'}\n')
			region.write(r'        \ncenter{1}'+'\n')
			region.write(r'        \centers{'+res[len(res)/2]+'}\n')
			region.write(r'        \nrespair{0}'+'\n')
			region.write('        \prop_trans_sig{1.e-4}\n\t\prop_rot_sig{1.e-5}\n\t\prop_trans_sig_freeres{0}\n\t\prop_rot_sig_freeres{0}\n\t\prop_trans_sig_respair{0}\n\t\prop_rot_sig_respair{0}\n\t\prop_trans_sig_respair_internal{0.0}\n\t\prop_rot_sig_respair_internal{0.0}\n]\n\n\n\n\n')			
		
		with open(args.xrna) as x:
			for line in x:
				if line[:10] == '<BasePairs':
					l = line.split("'")
					start, length, end = int(l[1]), int(l[3]), int(l[5])
					# check if the short loops are adjacent
					add_loop = []
					for loop in loops_short:
						if start+length in loop or end+1 in loop:
							add_loop += loop
					res = []
					for i in range(start, start+length) + range(end-length+1, end+1):
						res += ['{}:{}'.format(args.chain,i)]
					# consider loops
					res_loop = []
					for i in range(start, start+length) + range(end-length+1, end+1) + add_loop:
						res_loop += ['{}:{}'.format(args.chain,i)]
					
					region.write(r'~region[\element_top_type{residue}'+'\n')
					region.write(r'        \dependency_type{independent}'+'\n')
					region.write(r'        \nres{'+str(len(res_loop))+'}\n')
					region.write(r'        \residues{'+','.join(res_loop)+'}\n')
					region.write(r'        \ncenter{2}'+'\n')
					region.write(r'        \centers{'+'{}:{},{}:{}'.format(args.chain,str(start + length/2), args.chain, str(end - length/2))+'}\n')
					region.write(r'        \nrespair{'+str(length)+'}\n')
					for j in xrange(length):
						region.write(r'\residue_pair{'+'{}:{},{}:{}'.format(args.chain,str(start + j), args.chain, str(end - j))+'}\n')
					region.write('        \prop_trans_sig{1.e-4}\n\t\prop_rot_sig{1.e-5}\n\t\prop_trans_sig_freeres{0}\n\t\prop_rot_sig_freeres{0}\n\t\prop_trans_sig_respair{0}\n\t\prop_rot_sig_respair{0}\n\t\prop_trans_sig_respair_internal{0.0}\n\t\prop_rot_sig_respair_internal{0.0}\n]\n\n\n\n\n')


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


if __name__ == '__main__':
	main()
