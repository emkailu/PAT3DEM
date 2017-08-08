#!/usr/bin/env python

import os
import sys
import argparse
import subprocess

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <pdb>
	PCA.
	"""
	
	args_def = {'allatom':0}	
	parser = argparse.ArgumentParser()
	parser.add_argument("pdb", nargs='*', help="specify pdbs to be processed")
	parser.add_argument("-a", "--allatom", type=int, help="specify as 1 if you want to do all atom, by default {}, which only considers C4' and CA".format(args_def['allatom']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# merge all the input pdb into one
	pdbs='PCA-all.pdb'
	with open(pdbs,'w') as pdb_w:
		for i,pdb in enumerate(args.pdb):
			pdb_w.write('MODEL {:0>2d}\n'.format(i))
			with open(pdb) as pdb_r:
				if args.allatom == 1:
					for l in pdb_r.readlines():
						#if "C4'" in l or "CA" in l:
						pdb_w.write(l)
				else:
					for l in pdb_r.readlines():
						if "C4'" in l or "CA" in l:
							pdb_w.write(l)					
			pdb_w.write('ENDMDL\n')
	pcxray = 'pcxray.txt'	
	score='PCA-score.txt'
	eigenvalues='PCA-eigenvalues.txt'
	eigenvectors='PCA-eigenvectors.txt'
	traj1='PCA-traj1.pdb'
	traj2='PCA-traj2.pdb'
	traj3='PCA-traj3.pdb'
	with open('zz-PCA.R', 'w') as pca:
		pca.write("library(bio3d)\npdbs<-read.pdb('{}',multi=TRUE)\nxyz<-pdbs$xyz\npc.xray<-pca.xyz(xyz)\noptions(max.print=10000000)\nsink('{}')\npc.xray\nsink()\nsink('{}')\npc.xray$z\nsink()\nsink('{}')\npc.xray$L\nsink()\nsink('{}')\npc.xray$U\nsink()\nmktrj(pca = pc.xray, pc = 1, mag = 1, step = 0.125, file = '{}', pdb = pdbs, rock=TRUE)\nmktrj(pca = pc.xray, pc = 2, mag = 1, step = 0.125, file = '{}', pdb = pdbs, rock=TRUE)\nmktrj(pca = pc.xray, pc = 3, mag = 1, step = 0.125, file = '{}', pdb = pdbs, rock=TRUE)\n".format(pdbs,pcxray,score,eigenvalues,eigenvectors,traj1,traj2,traj3))
	# run the code
	with open('zz-PCA.log', 'w') as write_log:
		subprocess.call(['R', 'CMD', 'BATCH', 'zz-PCA.R'], stdout=write_log, stderr=subprocess.STDOUT)
	
	
				
if __name__ == '__main__':
	main()
