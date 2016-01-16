#!/usr/bin/env python

import os
import sys
import argparse
import pat3dem.cluster as p3c

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <*.pdb>
	Run rosetta.
	"""
	
	args_def = {'repeat':100, 'resolution':4, 'rosetta3':'/scratch/user/kailuyang/compile/rosetta_bin_linux_2015.39.58186_bundle/main'}	
	parser = argparse.ArgumentParser()
	parser.add_argument("pdb", nargs='*', help="specify pdb to be processed")
	parser.add_argument("-r", "--repeat", type=int, help="specify repeat, by default {}".format(args_def['repeat']))
	parser.add_argument("-re", "--resolution", type=float, help="specify reslution, by default {}".format(args_def['resolution']))
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
	# loop over input pdbs
	for i in args.pdb:
		basename = os.path.basename(os.path.splitext(i)[0])
		for j in xrange(args.repeat):
			out = '{}_repeat{:04}'.format(basename, j)
			with open('{}.sh'.format(out), 'w') as write_sh:
				write_sh.write('ROSETTA3={}\n'.format(args.rosetta3))
				write_sh.write('$ROSETTA3/source/bin/rosetta_scripts.linuxgccrelease \\\n')
				write_sh.write('    		-database $ROSETTA3/database/ \\\n')
				write_sh.write('    		-in::file::s {} \\\n'.format(i))
				write_sh.write('    		-parser::protocol refine.xml \\\n')
				write_sh.write('    		-parser::script_vars denswt=25 rms=1.5 reso={} map={}.mrc testmap={}.mrc \\\n'.format(args.resolution, basename, basename))
				write_sh.write('    		-ignore_unrecognized_res \\\n')
				write_sh.write('    		-edensity::mapreso {} \\\n'.format(args.resolution))
				write_sh.write('    		-default_max_cycles 200 \\\n')
				write_sh.write('    		-edensity::cryoem_scatterers \\\n')
				write_sh.write('    		-out::suffix _{} \\\n'.format(out))
				write_sh.write('    		-crystal_refine\n')
			# submit to cluster
			cmd = 'sh {}.sh'.format(out)
			walltime, cpu, ptile = 1, 1, 1
			p3c.ada(cmd, out, walltime, cpu, ptile)			
			
if __name__ == '__main__':
	main()
