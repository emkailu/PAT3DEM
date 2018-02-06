#!/usr/bin/env python

import os
import sys
import argparse
import subprocess
import numpy as np
import math
import pat3dem.star as p3s
import time

def extract_drift(driftfiles):
	# for each movie, get the S function of x,y,t
	drifts = {}
	for i in driftfiles:
		basename = os.path.basename(i).replace('_0-Patch-FitCoeff.log','')
		# array 1: global motion. frame #, x, y
		a1 = np.genfromtxt(i.replace('_0-Patch-FitCoeff','_0-Patch-Full'), usecols=[1,2], invalid_raise=False)
		a1 = a1[~np.isnan(a1).any(axis=1)]
		# array 2: global motion coefficient. 18 rows * 4 columns (x0-6,y0-6,x7-,y7-)
		a2 = np.genfromtxt(i, usecols=[0,1], invalid_raise=False)
		a2 = a2[~np.isnan(a2).any(axis=1)]
		# the value of key basename is a list of two arrays
		drifts[basename] = [a1,a2]
	return drifts

def calc_bf(Dose,Drift):
	#54.98972357 -10.71983742 -64.93503624
	if Drift < 0.173: # 0.173
		Drift = 0.173
	return 54.98972357 - 10.71983742 * Dose - 64.93503624 * math.log(Drift)

def calc_cf(frame):
	# use raw
	cf = [-1.39296, -1.2218230000000001, -1.233257, -1.289164, -1.2680439999999999, -1.302573, -1.3084910000000001, -1.3359399999999999, -1.328943, -1.3496220000000001, -1.3955500000000001, -1.372897, -1.4010659999999999, -1.4003909999999999, -1.4706129999999999, -1.4543740000000001, -1.5008509999999999, -1.540643, -1.550033, -1.5795809999999999, -1.5548029999999999, -1.6306830000000001, -1.679001, -1.6959040000000001, -1.725311, -1.668207, -1.770302, -1.7904949999999999, -1.7948500000000001, -1.913079, -1.877874, -1.8626309999999999, -1.918317, -1.9201379999999999, -1.9217150000000001, -1.9456770000000001, -1.7951440000000001, -1.9709460000000001]
	return cf[frame]

def bfactors(mn, x, y, drifts):
	basename = mn.split('/')[-1].replace('_movie.mrcs','')
	a1,a2=drifts[basename]
	'''
	a3,a4 = np.split(a2,2,axis=0) # for frames0-6 and frames7-
	Drift = np.zeros((38,2))
	for frame in range(7):
		for i in range(2):
			Drift[frame] += a3[0][i] * frame
			Drift[frame] += a3[1][i] * frame ** 2
			Drift[frame] += a3[2][i] * frame ** 3
			Drift[frame] += a3[3][i] * frame      * x
			Drift[frame] += a3[4][i] * frame ** 2 * x
			Drift[frame] += a3[5][i] * frame ** 3 * x
			Drift[frame] += a3[6][i] * frame      * x*x
			Drift[frame] += a3[7][i] * frame ** 2 * x*x
			Drift[frame] += a3[8][i] * frame ** 3 * x*x
			Drift[frame] += a3[9][i] * frame      * y
			Drift[frame] += a3[10][i] * frame ** 2 * y
			Drift[frame] += a3[11][i] * frame ** 3 * y
			Drift[frame] += a3[12][i] * frame      * y*y
			Drift[frame] += a3[13][i] * frame ** 2 * y*y
			Drift[frame] += a3[14][i] * frame ** 3 * y*y
			Drift[frame] += a3[15][i] * frame      * x*y
			Drift[frame] += a3[16][i] * frame ** 2 * x*y
			Drift[frame] += a3[17][i] * frame ** 3 * x*y	
	for frame in range(7,38):
		for i in range(2):
			Drift[frame] += a4[0][i] * frame
			Drift[frame] += a4[1][i] * frame ** 2
			Drift[frame] += a4[2][i] * frame ** 3
			Drift[frame] += a4[3][i] * frame      * x
			Drift[frame] += a4[4][i] * frame ** 2 * x
			Drift[frame] += a4[5][i] * frame ** 3 * x
			Drift[frame] += a4[6][i] * frame      * x*x
			Drift[frame] += a4[7][i] * frame ** 2 * x*x
			Drift[frame] += a4[8][i] * frame ** 3 * x*x
			Drift[frame] += a4[9][i] * frame      * y
			Drift[frame] += a4[10][i] * frame ** 2 * y
			Drift[frame] += a4[11][i] * frame ** 3 * y
			Drift[frame] += a4[12][i] * frame      * y*y
			Drift[frame] += a4[13][i] * frame ** 2 * y*y
			Drift[frame] += a4[14][i] * frame ** 3 * y*y
			Drift[frame] += a4[15][i] * frame      * x*y
			Drift[frame] += a4[16][i] * frame ** 2 * x*y
			Drift[frame] += a4[17][i] * frame ** 3 * x*y
	'''
	Drift = a1
	diff = np.diff(Drift, axis=0)
	InFrame = np.hypot(diff[:,0], diff[:,1]) # distance between frame i+1 and i is assumed to be the inframe drift of frame i
	# InFrame is 1*37 array
	# make it 1*38, assuming 38~37
	InFrame = np.append(InFrame, [InFrame[-1]], axis=0)
	bfs = '\ndata_perframe_bfactors\nloop_ \n_rlnMovieFrameNumber #1 \n_rlnBfactorUsedForSharpening #2 \n_rlnFittedInterceptGuinierPlot #3 \n'
	for i,inf in enumerate(InFrame):
		bfs += ' {} {} {} \n'.format(i+1,calc_bf(i+1,inf),calc_cf(i))
	bfs += '\n'
	return bfs

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <*Patch-FitCoeff.log>
	Perform resolution-dependent dose and per-movie-drift weighting.
	Prep1: make a new folder
	       mkdir polishPerMovie;cd polishPerMovie
	Prep2: link the intermediate maps (rootname: shiny-nodrift)
	       ln -s ../Refine3D/*_shiny-nodrift_*half?_class001_unfil.mrc .
	Prep3: no other files in polishPerMovie folder and go upper
	       rm *.star;cd ..
	"""
	
	args_def = {'apix':0.6575, 'bfile':'', 'polish':'', 'run':'','rootshiny':'shiny-nodrift'}	
	parser = argparse.ArgumentParser()
	parser.add_argument("drift", nargs='*', help="specify the Patch-FitCoeff.log files")
	parser.add_argument("-a", "--apix", type=float, help="specify apix, by default {}".format(args_def['apix']))
	parser.add_argument("-b", "--bfile", type=str, help="specify the old _bfactors.star file, by default {}".format(args_def['bfile']))
	parser.add_argument("-p", "--polish", type=str, help="specify the input data file for the old polish, e.x., Refine3D/run1_data-for-polish.star, by default {}".format(args_def['polish']))
	parser.add_argument("-r", "--run", type=str, help="specify the command file to run polish, by default {}".format(args_def['run']))
	parser.add_argument("-rs", "--rootshiny", type=str, help="specify the root name for polish, by default {}".format(args_def['rootshiny']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# extract drift information
	drifts = extract_drift(args.drift)
	print "Successfully read drift data for {} movies.".format(len(args.drift))
	# read the for-polish star file
	s_d = p3s.star_parse(args.polish, 'data_images')
	header = s_d['data_'] + s_d['loop_']
	header_len = len(header)
	with open(args.polish) as star_read:
		lines = star_read.readlines()[header_len:-1]
	lines = [line.split() for line in lines]
	print "Successfully read {} movie particles.".format(len(lines))
	# loop through each movie
	moviename,x,y = s_d['_rlnMicrographName'],s_d['_rlnCoordinateX'],s_d['_rlnCoordinateY']
	movie = ''
	movien = 0
	basename = os.path.basename(os.path.splitext(args.polish)[0])
	forpolish = 'polishPerMovie/{}.star'.format(basename)
	bff = 'polishPerMovie/{}_{}_bfactors.star'.format(basename,args.rootshiny)
	for i, line in enumerate(lines):
		mn = line[moviename].split('@')[-1]
		if mn != movie: # a new movie
			print "Found a new movie."
			if os.path.isfile(forpolish): # the forpolish file already exists
				print "Polish the previous movie first."
				fp.close() # close the file first
				# run relion_particle_polish
				subprocess.call(['sh', args.run])
				movien += 1
				print "Successfully polished movie {}.".format(movien)
				os.unlink(args.rootshiny+'.star')
			print "Start a new forpolish file."
			fp = open(forpolish,'w')
			fp.write(''.join(header))
			fp.write(' '.join(line) + '\n')
			# another important thing to do now is to write a new bfactor file
			with open(bff,'w') as bffw:
				bffw.write(bfactors(line[moviename],line[x],line[y],drifts))
			print "Wrote a bfactor file for the new movie."
			movie = mn
		else:
			fp.write(' '.join(line) + '\n')
	print "Polish the last movie."
	fp.close() # close the file first
	# run relion_particle_polish
	subprocess.call(['sh', args.run])
	movien += 1
	print "Successfully polished movie {}.".format(movien)
	os.unlink(args.rootshiny+'.star')		
				
if __name__ == '__main__':
	main()
