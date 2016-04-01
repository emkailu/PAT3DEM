#!/usr/bin/env python

import os
import sys
import argparse
import subprocess
from EMAN2 import *

def decim1(num):
	# return a list of floats with 1 decimal
	num_new = []
	for i in num:
		num_new += [float("{0:0.1f}".format(float(i)))]
	return num_new

def ctf_read(ctftxt):
	# return a list of values in ctftxt
	with open(ctftxt) as ctftxt_r:
		lines = ctftxt_r.readlines()
	if len(lines) != 6:
		print 'Please check {}!'.format(ctftxt)
		sys.exit()
	p1 = lines[3].replace(';', '').split()
	p2 = lines[5].split()
	return decim1([p1[6], p1[9], p1[12], p1[15], p2[6], p2[2], p2[1]])	

def ctf(image, com_par):
	# do ctf
	basename = os.path.basename(os.path.splitext(image)[0])
	# unify mrcs format to mrc format
	if image[-5:] == '.mrcs':
		image_link = basename+'.p3.mrc'
		try:
			os.symlink(image, image_link)
		except OSError:
			pass
	# check avg_frame	
	avg_frame = com_par['movie'].split('\n')[-1]
	basename = basename + avg_frame + '.p3'
	# generate the com file
	out = basename+'_ctffind4'
	o_com = out + '.com'
	o_log = out + '.log'
	with open(o_com, 'w') as o_com_w:
		o_com_w.write('{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n'.format('#!/bin/bash', 'ctffind << eof', image_link, com_par['movie'], basename+'.ctf', com_par['apix'], com_par['voltage'], com_par['cs'], com_par['ac'], 512, com_par['minres'], com_par['maxres'], com_par['mindef'], com_par['maxdef'], com_par['step'], 100, 'no', 'eof'))
	# run the com
	with open(o_log, 'w') as write_log:
		subprocess.call(['sh', o_com], stdout=write_log, stderr=subprocess.STDOUT)
	
def ctf_run(image, com_par):
	# control the running of ctf
	com_par['nimg'] = EMUtil.get_image_count(image)	
	basename = os.path.basename(os.path.splitext(image)[0])
	ctftxt = '{}{}.p3.txt'.format(basename, com_par['nimg'])
	# if ctftxt does not exist, start an initial run
	if not os.path.isfile(ctftxt):
		com_par['movie'] = 'yes\n{}'.format(com_par['nimg'])
		com_par['minres'], com_par['maxres'], com_par['mindef'], com_par['maxdef'], com_par['step'] = 50, 5, 1000, 50000, 500
		ctf(image, com_par)
	elif os.path.isfile(ctftxt):
		p1_minres, p1_maxres, p1_mindef, p1_maxdef, p2_maxres, p2_mindef, p2_maxdef = ctf_read(ctftxt)
		# set minres based on defocus
		if p2_maxdef > 25000:
			p2_minres = 40.0
		elif p2_maxdef > 12000:
			p2_minres = 30.0
		elif p2_maxdef > 7000:
			p2_minres = 25.0
		else:
			p2_minres = 20.0
		# for some bad images, you have to increase minres
		while p2_minres <= p2_maxres:
			p2_minres = p2_maxres + 1
		# if parameters converged
		if p2_minres == p1_minres and p2_maxres == p1_maxres and p2_mindef > p1_mindef and p2_maxdef < p1_maxdef or com_par['iter'] == 10:
			# test avg frames
			com_par['minres'], com_par['maxres'], com_par['mindef'], com_par['maxdef'], com_par['step'] = p2_minres, p2_maxres, p2_mindef-1000, p2_maxdef+2000, 100
			for i in xrange(1, com_par['nimg']):
				com_par['movie'] = 'yes\n{}'.format(i)
				ctf(image, com_par)
			# find the best avg
			d_def = {}
			best_ring = {}
			for i in xrange(1, com_par['nimg']+1):
				result = ctf_read('{}{}.p3.txt'.format(basename, i))
				d_def[i] = result[6]-result[5]
				best_ring[i] = result[4]
			# get an inverse dictionary
			inv = {}
			for k, v in d_def.iteritems():
				inv[v] = inv.get(v, []) + [k]
			# we prefer the smallest d_def
			find = 0
			for defocus in sorted(inv):
				# if d_def are the same, we prefer a larger avg
				for avg in sorted(inv[defocus], reverse=True):
					# if the best_ring didn't get worse, we find it!
					if best_ring[avg] <= best_ring[com_par['nimg']]:
						os.rename('{}{}.p3.txt'.format(basename, avg), '{}.txt'.format(basename))
						os.rename('{}{}.p3.ctf'.format(basename, avg), '{}.ctf'.format(basename))
						os.rename('{}{}.p3_ctffind4.log'.format(basename, avg), '{}_ctffind3.log'.format(basename))
						find = 1
						break
				if find == 1:
					break
			# append as ctffind3 format for relion
			with open('{}.txt'.format(basename)) as final_r:
				lines = final_r.readlines()
			line = lines[-1].split()
			df1, df2, ast, cc = line[1], line[2], line[3], line[5]
			xmag = com_par['dpsize'] * 10000 / com_par['apix']
			with open('{}_ctffind3.log'.format(basename), 'a') as final_w:
				final_w.write('CS[mm], HT[kV], AmpCnst, XMAG, DStep[um]\n')
				final_w.write('{} {} {} {} {}\n\n'.format(com_par['cs'], com_par['voltage'], com_par['ac'], xmag, com_par['dpsize']))
				final_w.write('DFMID1\tDFMID2\tANGAST\tCC\n')
				final_w.write('{} {} {} {} Final Values'.format(df1, df2, ast, cc))
			# delete intermediate files
			for i in glob.glob(basename + '*.p3.*'):
				os.unlink(i)
			for i in glob.glob(basename + '*.p3_*'):
				os.unlink(i)						
			return 'OK'			
		# else parameters haven't converged
		else:
			com_par['movie'] = 'yes\n{}'.format(com_par['nimg'])
			com_par['minres'], com_par['maxres'], com_par['mindef'], com_par['maxdef'], com_par['step'] = p2_minres, p2_maxres, p2_mindef-1000, p2_maxdef+2000, 100
			ctf(image, com_par)
			com_par['iter'] += 1	
			
def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <movie.mrcs>
	Run ctffind4 until parameters converge.
	Needs:
	'ctffind' command (v4.0.16, Rohou & Grigorieff, 2015)
	"""
	
	args_def = {'apix':1.25, 'voltage':200, 'cs':2, 'ac':0.1, 'dpsize':5}	
	parser = argparse.ArgumentParser()
	parser.add_argument("image", nargs='*', help="specify images to be processed")
	parser.add_argument("-a", "--apix", type=float, help="specify apix, by default {}".format(args_def['apix']))
	parser.add_argument("-v", "--voltage", type=int, help="specify the voltage (kV), by default {}".format(args_def['voltage']))
	parser.add_argument("-c", "--cs", type=float, help="specify spherical abberration, by default {}".format(args_def['cs']))
	parser.add_argument("-ac", "--ac", type=float, help="specify amplitude contrast, by default {}".format(args_def['ac']))
	parser.add_argument("-d", "--dpsize", type=float, help="specify detector pixel size (um), by default {}".format(args_def['dpsize']))
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
	com_par = {'apix':args.apix, 'voltage':args.voltage, 'cs':args.cs, 'ac':args.ac, 'dpsize':args.dpsize}
	# loop over all the input images
	for image in args.image:
		com_par['iter'] = 0
		status = ctf_run(image, com_par)
		while status != 'OK':
			status = ctf_run(image, com_par)
		
if __name__ == '__main__':
	main()
