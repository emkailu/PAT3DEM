#!/usr/bin/env python

import os
import sys
import argparse
import subprocess
import pat3dem.pdb as p3p

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <.ccp4>
	Automatically run erraser in single or multi residue mode. It runs faster because only nearby fragment will be used as input. After it's done, the refined fragment will be inserted back to the original pdb. The map is still the whole map.
	"""
	
	args_def = {'start':10, 'end':10, 'more5':0, 'more3':0, 'rebuild':'rebuild.txt'}	
	parser = argparse.ArgumentParser()
	parser.add_argument("ccp4", nargs='*', help="specify the map in ccp4 format to be processed")
	parser.add_argument("-s", "--start", type=int, help="specify the length at 5' side of the single residue, by default {}".format(args_def['start']))
	parser.add_argument("-e", "--end", type=int, help="specify the length at 3' side of the single residue, by default {}".format(args_def['end']))
	parser.add_argument("-m5", "--more5", type=int, help="specify the length, remodel i-m to i, by default {}".format(args_def['more5']))
	parser.add_argument("-m3", "--more3", type=int, help="specify the length, remodel i to i+m, by default {}".format(args_def['more3']))
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
		# get the fragment
		chain = lines_new[i][0]
		seq = int(lines_new[i][1:])
		start = seq - args.start
		end = seq + args.end
		frag = p3p.pdb_cut('init_{:04d}.pdb'.format(i), chain, start, end)
		with open('init_{:04d}_frag.pdb'.format(i), 'w') as fr:
			fr.write(''.join(frag))
		#
		out = 'reb_{:04d}'.format(i)
		if args.more5 == 0 and args.more3 == 0:
			with open(out+'.sh', 'w') as write_sh:
				write_sh.write('phenix.erraser init_{:04d}_frag.pdb {} single_res_mode=True rebuild_res_pdb={}\n'.format(i,args.ccp4[0],lines_new[i]))
		else:
			fix1 = '{}{}-{}'.format(chain, start, seq-args.more5-1)
			fix2 = '{}{}-{}'.format(chain, seq+args.more3+1, end)
			with open(out+'.sh', 'w') as write_sh:
				write_sh.write("phenix.erraser init_{:04d}_frag.pdb {} fixed_res='{} {}' rebuild_all=True\n".format(i,args.ccp4[0], fix1, fix2))
			
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
			os.rename('init_{:04d}_frag_{}.pdb'.format(i,num), 'init_{:04d}_frag.pdb'.format(i+1))
		else:
			os.rename('init_{:04d}_frag_0.pdb'.format(i), 'init_{:04d}_frag.pdb'.format(i+1))
		mlines = p3p.pdb_merge('init_{:04d}.pdb'.format(i), 'init_{:04d}_frag.pdb'.format(i+1), chain, start, end)
		with open('init_{:04d}.pdb'.format(i+1), 'w') as merge:
			merge.write(''.join(mlines))
							
if __name__ == '__main__':
	main()
