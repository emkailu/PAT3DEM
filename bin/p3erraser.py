#!/usr/bin/env python

import os
import sys
import argparse
import subprocess

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <.ccp4>
	Automatically run erraser in single residue mode.
	"""
	
	args_def = {'rebuild':'rebuild.txt'}	
	parser = argparse.ArgumentParser()
	parser.add_argument("ccp4", nargs='*', help="specify the map in ccp4 format to be processed")
	parser.add_argument("-r", "--rebuild", type=str, help="specify rebuild.txt, each line is like 'a130', chain a, res 130, from 5', rebuild will start from 3', by default {}".format(args_def['rebuild']))
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
	with open(args.rebuild) as r:
		lines = r.readlines()
	# reverse and clean up the lines
	lines_new = []
	for line in reversed(lines):
		line = line.strip()
		if line:
			lines_new +=[line]
	# start
	for i in xrange(len(lines_new)):
		out = 'reb_{:04d}'.format(i)
		with open(out+'.sh', 'w') as write_sh:
			write_sh.write('phenix.erraser init_{:04d}.pdb {} single_res_mode=True rebuild_res_pdb={}\n'.format(i,args.ccp4[0],lines_new[i]))
		with open(out+'.log', 'w') as write_log:
			subprocess.call(['sh', out+'.sh'], stdout=write_log, stderr=subprocess.STDOUT)
		# what if no good
		with open('erraser.log') as elog:
			if 'No alternative conformation is found' in elog.read():
				os.rename('init_{:04d}.pdb'.format(i), 'init_{:04d}.pdb'.format(i+1))
				os.rename('erraser.log', 'erraser_{:04d}.log'.format(i))
				continue
		# select and rename
		with open('validation.txt') as v:
			vlines=v.readlines()
		num=''		
		for vline in vlines:
			if 'model_' in vline and '!!' not in vline:
				vline=vline.split()
				num=vline[0][-1]
				break
		if num != '':
			os.rename('init_{:04d}_{}.pdb'.format(i,num), 'init_{:04d}.pdb'.format(i+1))
		else:
			os.rename('init_{:04d}_0.pdb'.format(i), 'init_{:04d}.pdb'.format(i+1))
							
if __name__ == '__main__':
	main()
