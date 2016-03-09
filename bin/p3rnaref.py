#!/usr/bin/env python

import os
import sys
import argparse
import subprocess

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <rna.pdb>
	Refine the rna.pdb into a density map. The strategy is to refine from low resolution to high resolution with strict restraints of secondary structures.
	Needs:
	relion (v1.4, Scheres, 2012)
	Phenix
	"""
	
	args_def = {'apix':1.25, 'res':'10 4', 'mrc':'zz.mrc', 'eff':''}	
	parser = argparse.ArgumentParser()
	parser.add_argument("rna", nargs='*', help="specify rna.pdb to be processed")
	parser.add_argument("-a", "--apix", type=str, help="specify apix, by default {}".format(args_def['apix']))
	parser.add_argument("-r", "--res", type=str, help="specify a resolution range, by default '{}'".format(args_def['res']))
	parser.add_argument("-m", "--mrc", type=str, help="specify the density map in mrc format, by default '{}'".format(args_def['mrc']))
	parser.add_argument("-e", "--eff", type=str, help="specify the parameter file, by default {}".format(args_def['eff']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# Get low-pass filtered maps
	res_low, res_high = args.res.split()
	res_low, res_high = float(res_low), float(res_high)
	basename = os.path.basename(os.path.splitext(args.mrc)[0])
	model = args.rna[0]
	bn_model = os.path.basename(os.path.splitext(model)[0])
	while res_low >= res_high:
		lp = '{}_lp{}.mrc'.format(basename, res_low)
		low = str(res_low)
		with open(basename+'_lp.log', 'a') as write_log:
			subprocess.call(['relion_image_handler', '--i', args.mrc, '--o', lp, '--angpix', str(args.apix), '--lowpass', low], stdout=write_log, stderr=subprocess.STDOUT)
		with open(basename+'_ref.log', 'a') as ref_log:
			subprocess.call(['phenix.real_space_refine', model, lp, args.eff, 'resolution='+low, 'run=minimization_global+local_grid_search+morphing+simulated_annealing'], stdout=ref_log, stderr=subprocess.STDOUT)
		model = '{}_lp{}.pdb'.format(bn_model, res_low)
		os.rename(bn_model+'_real_space_refined.pdb', model)
		bn_model = os.path.basename(os.path.splitext(model)[0])
		res_low -= 2
				
if __name__ == '__main__':
	main()
