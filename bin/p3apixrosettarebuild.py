#!/usr/bin/env python

import os
import sys
import argparse
import subprocess
import pat3dem.pdb as p3p
import scipy.optimize as opt
from EMAN2 import *

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <input>
	Alternate 1) rosetta refinement of a model and 2) apix optimization of a map iteratively until the apix converges.
	"""
	
	args_def = {'apix':1.216, 'iter':100, 'resolution':3.3, 'rosetta3':'/home/kailuyang/scratch/compile/rosetta_bin_linux_2017.08.59291_bundle/main'}	
	parser = argparse.ArgumentParser()
	parser.add_argument("input", nargs='*', help="specify input to be processed")
	parser.add_argument("-a", "--apix", type=float, help="specify apix, by default {}".format(args_def['apix']))
	parser.add_argument("-i", "--iter", type=int, help="specify iterations, by default {}".format(args_def['iter']))
	parser.add_argument("-r", "--resolution", type=float, help="specify reslution, by default {}".format(args_def['resolution']))	
	parser.add_argument("-r3", "--rosetta3", type=str, help="specify rosetta3, by default {}".format(args_def['rosetta3']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# get common parameters
	c_p = {'apix':args.apix, 'res':args.resolution, 'boxsize':EMData('map_0000.mrc')["nx"]}
	# iterate for args.iter cycles
	for i in xrange(args.iter):
		out = 'ref_{:04d}'.format(i)
		# run rosetta refinement
		with open(out+'.sh', 'w') as write_sh:
			write_sh.write('ROSETTA3={}\n'.format(args.rosetta3))
			write_sh.write('$ROSETTA3/source/bin/rosetta_scripts.static.linuxgccrelease \\\n')
			write_sh.write('    		-database $ROSETTA3/database/ \\\n')
			write_sh.write('    		-in::file::s init_{:04d}.pdb \\\n'.format(i))
			write_sh.write('    		-parser::protocol ../asym-ref.xml \\\n')
			write_sh.write('    		-parser::script_vars denswt=35 rms=1.5 reso={} map=map_{:04d}.mrc testmap=map_{:04d}.mrc \\\n'.format(args.resolution, i, i))
			write_sh.write('    		-ignore_unrecognized_res \\\n')
			write_sh.write('    		-edensity::mapreso {} \\\n'.format(args.resolution))
			write_sh.write('    		-default_max_cycles 200 \\\n')
			write_sh.write('    		-edensity::cryoem_scatterers \\\n')
			write_sh.write('    		-crystal_refine\n')		
		with open(out+'.log', 'w') as write_log:
			subprocess.call(['sh', out+'.sh'], stdout=write_log, stderr=subprocess.STDOUT)
		# rename
		os.rename('score.sc', 'score_{:04d}.sc'.format(i))
		os.rename('init_{:04d}_0001.pdb'.format(i), 'init_{:04d}.pdb'.format(i+1))
		# run apix optimization
		f = lambda x: ccc(x, i, c_p)
		rranges = [slice(args.apix-0.15, args.apix+0.15, 0.01)]
		resbrute = opt.brute(f, rranges, full_output=True, finish=opt.fmin)
		x_res, y_res = resbrute[0][0], resbrute[1]
		print x_res, y_res
		# generate new map using new apix and align it to new pdb
		ali=ccc_align(x_res,i,c_p)
		ali.write_image('map_{:04d}.mrc'.format(i+1))
		
def ccc(x,i,c_p):
	ali=ccc_align(x,i,c_p)
	return ali['score']

def ccc_align(x,i,c_p):
	# now the apix is assumed to be x
	x = float(x)
	# convert pdb to mrc using apix=x
	outmap = p3p.pdb2mrc('init_{:04d}.pdb'.format(i+1),x,c_p['res'],False,c_p['boxsize'],None,True)
	# read map and (no need to) change apix
	d = EMData('map_{:04d}.mrc'.format(i))
	d.set_attr('apix_x', x)
	d.set_attr('apix_y', x)
	d.set_attr('apix_z', x)
	ali=d.align('refine_3d',outmap,{},'ccc',{})
	return ali
	
if __name__ == '__main__':
	main()
