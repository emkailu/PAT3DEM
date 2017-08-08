#!/usr/bin/env python

from EMAN2 import *
from math import *
import os
import sys
from Bio.PDB import *

atomdefs={'H':(1.0,1.00794),'C':(6.0,12.0107),'A':(7.0,14.00674),'N':(7.0,14.00674),'O':(8.0,15.9994),'P':(15.0,30.973761),'S':(16.0,32.066),'W':(18.0,1.00794*2.0+15.9994),'AU':(79.0,196.96655) }

def pdb_lines(pdb):
	# convert a pdb file to lines
	with open(pdb) as p:
		lines = p.readlines()
	return lines

def pdb_line_num(lines, chain, start, end):
	# return sline and eline, corresponding to chain start and end
	liner = xrange(len(lines))
	for i in liner:
		line = lines[i]
		if line[:4] == 'ATOM':
			if line[21] == chain:
				if int(line[22:26]) == start:
					sline = i
					break
	for j in reversed(liner):
		line = lines[j]
		if line[:4] == 'ATOM':
			if line[21] == chain:
				if int(line[22:26]) == end:
					eline = j
					break
	try:
		sline, eline
	except NameError:
		exit("well, the start and/or end residue of the chain does not exist!")
	return sline, eline	

def pdb_merge(pbig, pfrag, chain, start, end):
	# replace pbig chain from start to end, by pfrag
	pbiglines = pdb_lines(pbig)
	pfraglines = pdb_lines(pfrag)
	sline,eline = pdb_line_num(pbiglines, chain, start, end)
	sline2,eline2 = pdb_line_num(pfraglines, chain, start, end)
	return pbiglines[:sline] + pfraglines[sline2:eline2+1] + pbiglines[eline+1:]

def pdb_cut(pdb, chain, start, end):
	# return lines of the pdb containing residues between start and end
	lines = pdb_lines(pdb)
	sline,eline = pdb_line_num(lines, chain, start, end)
	return lines[sline:eline+1]

def pdb_cut_2frag(lines, chain, num):
	# return lines after del num_list, divide into 2 frags
	# num must have 4 numbers
	num.sort(key=int)
	# lines2 first
	sline2,eline2 = pdb_line_num(lines, chain, num[1]+1, num[2]-1)
	lines2 = lines[sline2:eline2+1]
	
	sline1_1,eline1_1 = pdb_line_num(lines, chain, num[0], num[0])
	sline1_2,eline1_2 = pdb_line_num(lines, chain, num[-1], num[-1])
	del lines[sline1_1:eline1_2+1]
	
	return lines,lines2

def pdb_del(lines, chain, num):
	# return lines of the pdb after deleting residues in the num list
	num.sort(key=int)
	for res in num:
		sline,eline = pdb_line_num(lines, chain, res, res)
		del lines[sline:eline+1]
	return lines

def pdb_ss_atom(pdb):
	# write a new pdb file, which contains the secondary structures and atoms
	basename = os.path.basename(os.path.splitext(pdb)[0])
	with open(basename + '_ss_atom.pdb', 'w') as write_ss_atom:
		with open(pdb) as read_pdb:
			for i in read_pdb.readlines():
				if i[:5] in ['HELIX', 'SHEET']:
					write_ss_atom.write(i)
				if i[:4] == 'ATOM' or i[:6] == 'HETATM':
					write_ss_atom.write(i)
					
def aa_3to1(aa):
	# return the one-letter (upper case) abbreviation of the input three-letter (not case-sensitive)
	aa_dict = {'ALA':'A', 'ARG':'R', 'ASN':'N', 'ASP':'D', 'CYS':'C', 'GLN':'Q', 'GLU':'E', 'GLY':'G', 'HIS':'H', 'ILE':'I', 'LEU':'L', 'LYS':'K', 'MET':'M', 'PHE':'F', 'PRO':'P', 'SER':'S', 'THR':'T', 'TRP':'W', 'TYR':'W', 'VAL':'V', 'A':'A', 'U':'U', 'C':'C', 'G':'G', 'LIG':'j'}# small j for ligand
	return aa_dict[aa.strip().upper()]

def pdb_get_seq(pdb, chain):
	# return a dictionary, {residue #: AA}
	with open(pdb) as read_pdb:
		seq = {}
		for i in read_pdb.readlines():
			if i[21] == chain:
				if i[:4] == 'ATOM' or i[:6] == 'HETATM': 
					seq[i[22:26].strip()] = aa_3to1(i[17:20])
	return seq

def pdb_CA(pdb):
	# return two lists of CA and C4' of the input pdb
	CA = []
	# CA27 to store the first 18-27 characters of each line that contains CA
	CA27 = []
	with open(pdb) as p:
		lines = p.readlines()
	for i in lines:
		if i[13:15] == 'CA' or i[13:16] == "C4'":
			if i[:4] == 'ATOM': 
				CA += [i]
				CA27 += [i[17:27]]
	return CA, CA27

def get_coord(l):
	# return the coordinates (x, y, z) of a line from pdb file
	return float(l[30:38]), float(l[38:46]), float(l[46:54])

def sup(fix,move):
	p = PDBParser()
	s_fix = p.get_structure('fix', fix)
	a_fix = Selection.unfold_entities(s_fix, 'A')
	p2 = PDBParser()
	s_move = p2.get_structure('move', move)
	a_move = Selection.unfold_entities(s_move, 'A')
	sup = Superimposer()
	sup.set_atoms(a_fix, a_move)
	return sup

# this function is copied from EMAN2 with minor modification
# this function originally added so that it could be accessed independently (for Junjie Zhang by David Woolford)
def pdb2mrc(file_name,apix=1.0,res=2.8,het=False,box=None,chains=None,quiet=False):
	'''
	file_name is the name of a pdb file
	apix is the angstrom per pixel
	res is requested resolution, quivalent to Gaussian lowpass with 1/e width at 1/res
	het is a flag inidicating whether HET atoms should be included in the map
	box is the boxsize, can be a single int (e.g. 128), a tuple (e.g. [128,64,54]), or a string (e.g. "128" or "128,64,57")
	chains is a string list of chain identifiers, eg 'ABEFG'
	quiet can be used to turn of helpful print outs
	'''
	
	try : infile=open(file_name,"r")
	except : raise IOError("%s is an invalid file name" %file_name)
	
	
	if res<=apix : print "Warning: res<=apix. Generally res should be 2x apix or more"
	
	aavg=[0,0,0]	# calculate atomic center
	amin=[1.0e20,1.0e20,1.0e20]		# coords of lower left front corner of bounding box
	amax=[-1.0e20,-1.0e20,-1.0e20]	# coords
	natm=0
	atoms=[]		# we store a list of atoms to process to avoid multiple passes
	nelec=0
	mass=0

	# parse the pdb file and pull out relevant atoms
	for line in infile:
		if (line[:4]=='ATOM' or (line[:6]=='HETATM' and het)) :
			if chains and not (line[21] in chains) : continue
			try:
				a=line[12:14].strip()
				if a[-1] == 'H':
					#a = 'H'
					continue # skip H
				aseq=int(line[6:11].strip())
				resol=int(line[22:26].strip())
	
				x=float(line[30:38])
				y=float(line[38:46])
				z=float(line[46:54])
			except:
				print "PDB Parse error:\n%s\n'%s','%s','%s'  '%s','%s','%s'\n"%(
					line,line[12:14],line[6:11],line[22:26],line[30:38],line[38:46],line[46:54])
				print a,aseq,resol,x,y,z

			atoms.append((a,x,y,z))
						
			aavg[0]+=x
			aavg[1]+=y
			aavg[2]+=z
			natm+=1
			
			amin[0]=min(x,amin[0])
			amin[1]=min(y,amin[1])
			amin[2]=min(z,amin[2])
			amax[0]=max(x,amax[0])
			amax[1]=max(y,amax[1])
			amax[2]=max(z,amax[2])

			try:
				nelec+=atomdefs[a.upper()][0]
				mass+=atomdefs[a.upper()][1]
			except:
				print("Unknown atom %s ignored at %d"%(a,aseq))
							
	infile.close()
	
	if not quiet:
		print "%d atoms used with a total charge of %d e- and a mass of %d kDa"%(natm,nelec,mass/1000)
		print "atomic center at %1.1f,%1.1f,%1.1f (center of volume at 0,0,0)"%(aavg[0]/natm,aavg[1]/natm,aavg[2]/natm)
		print "Bounding box: x: %7.2f - %7.2f"%(amin[0],amax[0])
		print "              y: %7.2f - %7.2f"%(amin[1],amax[1])
		print "              z: %7.2f - %7.2f"%(amin[2],amax[2])
	
	# precalculate a prototypical Gaussian to resample
	# 64^3 box with a real-space 1/2 width of 12 pixels
	gaus=EMData()
	gaus.set_size(64,64,64)
	gaus.to_one()
	
	gaus.process_inplace("mask.gaussian",{"outer_radius":12.0})

	# find the output box size, either user specified or from bounding box
	outbox=[0,0,0]
	try:
		# made
		if isinstance(box,int):
			outbox[0]=outbox[1]=outbox[2]=box
		elif isinstance(box,list):
			outbox[0]=box[0]
			outbox[1]=box[1]
			outbox[2]=box[2]
		else:
			spl=box.split(',')
			if len(spl)==1 : outbox[0]=outbox[1]=outbox[2]=int(spl[0])
			else :
				outbox[0]=int(spl[0])
				outbox[1]=int(spl[1])
				outbox[2]=int(spl[2])
	except:
		pad=int(2.0*res/apix)
		outbox[0]=int((amax[0]-amin[0])/apix)+pad
		outbox[1]=int((amax[1]-amin[1])/apix)+pad
		outbox[2]=int((amax[2]-amin[2])/apix)+pad
		outbox[0]+=outbox[0]%2
		outbox[1]+=outbox[1]%2
		outbox[2]+=outbox[2]%2
		
	if not quiet: print "Box size: %d x %d x %d"%(outbox[0],outbox[1],outbox[2])
	
	# initialize the final output volume
	outmap=EMData()
	outmap.set_size(outbox[0],outbox[1],outbox[2])
	outmap.to_zero()	
	for i in range(len(aavg)): aavg[i] = aavg[i]/float(natm)	
	# fill in the atom gaussians
	xt = outbox[0]/2 - (amax[0]-amin[0])/(2*apix)
	yt = outbox[1]/2 - (amax[1]-amin[1])/(2*apix)
	zt = outbox[2]/2 - (amax[2]-amin[2])/(2*apix)
	for i,a in enumerate(atoms):
		if not quiet and i%1000==0 : 
			print '\r   %d'%i,
			sys.stdout.flush()
		try:
			# This insertion strategy ensures the output is centered.
			elec=atomdefs[a[0].upper()][0]
			outmap.insert_scaled_sum(gaus,(a[1]/apix+xt-amin[0]/apix,a[2]/apix+yt-amin[1]/apix,a[3]/apix+zt-amin[2]/apix),res/(pi*12.0*apix),elec)
		except: print "Skipping %d '%s'"%(i,a[0])		
	if not quiet: print '\r   %d\nConversion complete'%len(atoms)		
	outmap.set_attr("apix_x",apix)
	outmap.set_attr("apix_y",apix)
	outmap.set_attr("apix_z",apix)	
	outmap.set_attr("origin_x",-xt*apix+amin[0])	
	outmap.set_attr("origin_y",-yt*apix+amin[1])	
	outmap.set_attr("origin_z",-zt*apix+amin[2])
	return outmap
