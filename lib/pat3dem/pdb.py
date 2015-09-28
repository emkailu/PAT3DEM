#!/usr/bin/env python

import os

def pdb_ss_atom(pdb):
	# write a new pdb file, which contains the secondary structures and atoms
	basename = os.path.basename(os.path.splitext(pdb)[0])
	with open(basename + '_ss_atom.pdb', 'w') as write_ss_atom:
		with open(pdb) as read_pdb:
			for i in read_pdb.readlines():
				if i[:5] in ['HELIX', 'SHEET']:
					write_ss_atom.write(i)
				if i[:6].strip() in ['ATOM', 'HETATM']:
					write_ss_atom.write(i)
					
def aa_3to1(aa):
	# return the one-letter (upper case) abbreviation of the input three-letter (not case-sensitive)
	aa_dict = {'ALA':'A', 'ARG':'R', 'ASN':'N', 'ASP':'D', 'CYS':'C', 'GLN':'Q', 'GLU':'E', 'GLY':'G', 'HIS':'H', 'ILE':'I', 'LEU':'L', 'LYS':'K', 'MET':'M', 'PHE':'F', 'PRO':'P', 'SER':'S', 'THR':'T', 'TRP':'W', 'TYR':'W', 'VAL':'V'}
	return aa_dict[aa.upper()]

def pdb_get_seq(pdb, chain):
	# return a dictionary, {residue #: AA}
	with open(pdb) as read_pdb:
		seq = {}
		for i in read_pdb.readlines():
			if i[:6].strip() in ['ATOM', 'HETATM'] and i[21] == chain:
				seq[i[22:26].strip()] = aa_3to1(i[17:20])
	return seq

def pdb_CA(pdb):
	# return two lists of CA of the input pdb
	CA = []
	# CA27 to store the first 27 characters of each line that contains CA
	CA27 = []
	with open(pdb) as p:
		lines = p.readlines()
	for i in lines:
		if i[:6].strip() in ['ATOM', 'HETATM'] and i[13:15] == 'CA':
			CA += [i]
			CA27 += [i[:27]]
	return CA, CA27

def get_coord(l):
	# return the coordinates (x, y, z) of a line from pdb file
	return float(l[30:38]), float(l[38:46]), float(l[46:54])

