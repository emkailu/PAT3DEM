#!/usr/bin/env python

import os
import sys
import argparse
import subprocess
import random
import pat3dem.pdb as p3p
from Bio.PDB import *
from EMAN2 import *
from shutil import move

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <init.pdb>
	Mimic MOSAICS-EM. Use Rosetta de novo RNA sampling to replace MOSAICS.
	"""
	
	args_def = {'fasta':'handle.fasta','secstruct':'handle.secstruct','iter':1,'flexfile':'handle.flex', 'mrc':'', 'res':6, 'fix':'','move':''}	
	parser = argparse.ArgumentParser()
	parser.add_argument("pdb", nargs='*', help="specify pdb to be processed")
	parser.add_argument("-f", "--fasta", type=str, help="specify sequence fasta, by default {}".format(args_def['fasta']))
	parser.add_argument("-s", "--secstruct", type=str, help="specify secondary structure, by default {}".format(args_def['secstruct']))
	parser.add_argument("-i", "--iter", type=int, help="specify iterations, by default {}".format(args_def['iter']))
	parser.add_argument("-ff", "--flexfile", type=str, help="specify flexfile, by default {}".format(args_def['flexfile']))
	parser.add_argument("-m", "--mrc", type=str, help="specify mrc, by default {}".format(args_def['mrc']))
	parser.add_argument("-r", "--res", type=float, help="specify resolution, by default {}".format(args_def['res']))
	parser.add_argument("-fx", "--fix", type=str, help="specify fixed pdb for calculating matrix, by default {}".format(args_def['fix']))
	parser.add_argument("-mv", "--move", type=str, help="specify moving pdb for calculating matrix, by default {}".format(args_def['move']))
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
	# prepare files for rosetta de novo modeling
	# get working res
	with open(args.fasta) as f:
		lines = f.readlines()
	line = lines[0].split()
	workres = ' '.join(line[1:])
	# get flexes
	with open(args.flexfile) as f:
		flexes = f.readlines()
	flexes_new = []
	for i in flexes:
		i = i.split(',')
		j = [int(x) for x in i] # from str list to int list
		flexes_new.append(j) # list of list
	
	# get matrix to superimpose pdb
	sup = p3p.sup(args.fix,args.move)
	# get EMData
	d = EMData(args.mrc)
	boxsize = d["nx"]
	apix = d["apix_x"]
	# link
	os.symlink(args.pdb[0],'denovo000000.pdb')
	# # superimpose initial model
	suped = supout('denovo000000.pdb',sup)
	# calculate EM score
	pa=PointArray()
	pa.read_from_pdb(suped)
	out=pa.pdb2mrc_by_summation(boxsize,apix,args.res,-1)
	c = d.cmp("ccc",out)	
	# write the setup.sh
	for i in xrange(args.iter):
		with open('denovo{:06d}.pdb'.format(i)) as f:
			pdblines=f.readlines()		
		flex,lines1,lines2 = gen_frag(pdblines,flexes_new)
		if flex[0] == 1561:
			args.secstruct += '.1561'
		elif flex[0] == 1567:
			args.secstruct += '.1567'
		else:
			args.secstruct += '.1573'
		frag1 = 'frag_{:06d}_1.pdb'.format(i)
		with open(frag1,'w') as fw:
			fw.write(''.join(lines1))
		frag2 = 'frag_{:06d}_2.pdb'.format(i)
		with open(frag2,'w') as fw:
			fw.write(''.join(lines2))		
		sh = 'setup_{:06d}.sh'.format(i)
		with open(sh,'w') as shw:
			shw.write("rna_denovo_setup.py -out:file:silent -nstruct 1 -fasta {} -secstruct_file {} -working_res {} -no_minimize -cycles 20000 -ignore_zero_occupancy false -tag {} -s {} {}".format(args.fasta,args.secstruct,workres, 'denovo{:06d}'.format(i), frag1, frag2))
		subprocess.call(['sh', sh])
		subprocess.call(['sh', 'README_FARFAR'])
		# extract
		if os.path.isfile('denovo{:06d}.out'.format(i)):
			subprocess.call(['~/scratch/compile/rosetta_bin_linux_2016.13.58602_bundle/main/source/bin/rna_extract.linuxgccrelease', '-in:file:silent','denovo{:06d}.out'.format(i), '-in:file:silent_struct_type', 'rna'])
		else:
			print 'Iteration {}, failed.'.format(i)
			move('denovo{:06d}.pdb'.format(i), 'denovo{:06d}.pdb'.format(i+1))
			continue
		# superimpose output
		os.rename('S_000001.pdb','denovo{:06d}.pdb'.format(i+1))
		suped = supout('denovo{:06d}.pdb'.format(i+1),sup)
		# calculate EM score
		pa=PointArray()
		pa.read_from_pdb(suped)
		out=pa.pdb2mrc_by_summation(boxsize,apix,args.res,-1)
		c_new = d.cmp("ccc",out)
		# is it better?
		if c_new < c:
			c = c_new
			print 'Iteration {}, {} is better than {}.'.format(i,c_new,c)
		else:
			print 'Iteration {}, {} is worse than {}.'.format(i,c_new,c)
			move('denovo{:06d}.pdb'.format(i), 'denovo{:06d}.pdb'.format(i+1))
	
def gen_frag(pdblines,flexes):
	# flex is a list of 4 flexible residues that defines a reasonable flexible region where de novo modeling will be performed. e.g., [1553, 1553,1652,1652], [1553,1554,1651,1652]
	# Here a test of acceptance ratio
	f1 = [1561,1566,1637,1642]
	f2 = [1567,1572,1636,1632]
	f3 = [1573,1576,1628,1631]
	flex = random.choice([f1,f2,f3])
	lines1,lines2 = p3p.pdb_cut_2frag(pdblines, 'A', flex)
	return flex,lines1,lines2

def supout(pdb,sup):
	suped = pdb+'_sup.pdb'
	p = PDBParser()
	s_move = p.get_structure('move', pdb)
	a_move = Selection.unfold_entities(s_move, 'A')
	sup.apply(a_move)
	io = PDBIO()
	io.set_structure(s_move)
	io.save(suped)
	return suped
	
if __name__ == '__main__':
	main()
