#!/usr/bin/env python

import os
import sys
import argparse
import subprocess
from EMAN2 import *

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <movies>
	output fulldose, and optionally lowdose, lowdose movies
	needs:
	dosefgpu_driftcorr (for superresolution only) (v2.0, Li et al., 2013)
	unblur (v1.0.2, Grant & Grigorieff, 2015)
	EMAN2 (v2.11, Tang et al., 2007)
	relion (v1.4, Scheres, 2012)
	"""
	
	parser = argparse.ArgumentParser()
	parser.add_argument("movie", nargs='*', help="specify movies to be processed")
	parser.add_argument("-a", "--apix", type=float, help="specify apix, by default 1.25")
	parser.add_argument("-t", "--time", type=float, help="specify exposure time per frame in ms, by default 200")
	parser.add_argument("-r", "--rate", type=float, help="specify dose rate in e/pix/s (counting pixel, not superresolution), by default 5")
	parser.add_argument("-s", "--save", type=int, help="save a specified number (multiples of 4) of aligned frames, by default 0, which means do not save")
	parser.add_argument("-x", "--xsuper", type=int, help="specify the x dimension of superresolution images, by default 7420")
	args_default = {'apix':1.25, 'time':200, 'rate':5, 'save':0, 'xsuper':7420}
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options"
		sys.exit(1)	
	else:
		# get default values
		for i in args_default:
			if args.__dict__[i] == None:
				args.__dict__[i] = args_default[i]
		# loop over all the input movies		
		for movie in args.movie:
			# first unify the files to mrcs format
			basename = os.path.basename(os.path.splitext(movie)[0])
			if movie[-4:] == '.dm4':
				subprocess.call(['e2proc2d.py', movie, basename+'_dm4.mrcs'])
				movie = basename+'_dm4.mrcs'
				basename = os.path.basename(os.path.splitext(movie)[0])
			elif movie[-4:] == '.mrc':
				subprocess.call(['ln', '-s', movie, basename+'.mrcs'])
				movie = basename+'.mrcs'
			# then unify the superresolution to counting	
			d=EMData(movie)
			if d["nx"] == args.xsuper:
				subprocess.call(['dosefgpu_driftcorr', movie, '-bin', '2', '-ssr', '1', '-frt', basename+'_2x.mrcs', '-slg', '0', '-dsp', '0'])
				os.remove(basename+'_2x_SumCorr.mrc')
				if movie[-9:] == '_dm4.mrcs':
					os.remove(movie)
				movie = basename+'_2x.mrcs'
				basename = os.path.basename(os.path.splitext(movie)[0])
			# unblur
			softlink = 'ln -s ' + movie + ' ' + basename + '.mrc\n'
			unblur = 'unblur << eof\n'
			in_movie = basename + '.mrc\n'
			nimg = EMUtil.get_image_count(movie)
			out_sum = basename+'_fulldose.mrc\n'
			out_shift = basename+'_fulldose_shifts.txt\n'
			out_movie = basename+'_fulldose_movie.mrc'
			dose_filter = 'yes\n'
			dose = args.time/1000.0 * args.rate / args.apix ** 2
			with open(basename + '_unblur.com', 'w') as write_com:
				if args.save == 0:
					write_com.write(softlink + unblur + in_movie + str(nimg)+'\n' + out_sum + out_shift + str(args.apix)+'\n' + dose_filter + str(dose)+'\n' + '200\n' + '0\n' + 'no\n' + 'no\n' + 'eof\n')
				else:
					write_com.write(softlink + unblur + in_movie + str(nimg)+'\n' + out_sum + out_shift + str(args.apix)+'\n' + dose_filter + str(dose)+'\n' + '200\n' + '0\n' + 'yes\n' + out_movie+'\n' + 'no\n' + 'eof\n')
			with open(basename + '_unblur.log', 'w') as write_log:
				subprocess.call(['sh', basename + '_unblur.com'], stdout=write_log, stderr=subprocess.STDOUT)
			if movie[-9:] == '_dm4.mrcs' or movie[-8:] == '_2x.mrcs':
				os.remove(movie)
			if args.save != 0 and args.save%4 == 0:
				# extract the specified number (multiples of 4) of aligned frames
				subprocess.call(['e2proc2d.py', out_movie,  out_movie+'s', '--last', str(args.save-1)])
				os.remove(out_movie)
				# average every 4 frames and output lowdose movie
				subprocess.call(['relion_image_handler', '--i', out_movie+'s', '--o', basename+'_lowdose_movie.mrcs', '--avg_bin', '4'])
				os.remove(out_movie+'s')
				# generate lowdose sum
				subprocess.call(['relion_image_handler', '--i', basename+'_lowdose_movie.mrcs', '--o', basename+'_lowdose.mrc', '--avg_first', '1', '--avg_last', str(args.save/4)])
				
if __name__ == '__main__':
	main()
