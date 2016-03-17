#!/usr/bin/env python

import os
import sys
import argparse
import subprocess
import glob
from EMAN2 import *

def file_base(movie):
	# return the filename and basename, exclude '.p3'
	return movie, os.path.basename(os.path.splitext(movie)[0]).replace('.p3', '')

def run_unblur(in_movie, root, com_par):
	unblur = 'unblur << eof'
	basename = os.path.basename(os.path.splitext(in_movie)[0])
	# remove '.p3', '_unfil_movie', if it's in the basename
	basename = basename.replace('.p3', '')
	basename = basename.replace('_unfil_movie', '')
	out = basename + '_' + root
	out_sum = out + '.mrc'
	out_shift = out + '_shifts.txt'
	out_movie = out + '_movie.p3.mrc'
	com = out + '_unblur.com'
	log = out + '_unblur.log'
	expert = 'no'
	if root == 'unfil':
		save_movie = 'yes\n'+out_movie
		dose_filter = 'no'		
	elif root == 'fulldose':
		pre_exp = '0'			
		dose_filter = '\n'.join(['yes', com_par['dose'], com_par['voltage'], pre_exp])
		if com_par['save'] != '0 0 0':
			save_movie = 'yes\n'+out_movie
		else:
			save_movie = 'no'
	with open(com, 'w') as write_com:
		write_com.write('\n'.join([unblur, in_movie, str(com_par['nimg']), out_sum, out_shift, com_par['apix'], dose_filter, save_movie, expert, 'eof']))
	with open(log, 'w') as write_log:
		subprocess.call(['sh', com], stdout=write_log, stderr=subprocess.STDOUT)
	return out_movie

def get_ld(in_movie, root, com_par):
	# get lowdose from _fulldose_movie.mrcs
	basename = in_movie.replace('_fulldose_movie.p3.mrcs', '')
	out = basename + '_' + root
	ld_movie = out + '_movie.mrcs'
	ld_sum = out + '.mrc'
	# lowdose movie
	n = (com_par['last']-com_par['first']+1)/com_par['avg_bin']
	for i in xrange(n):
		avg=Averagers.get("mean")
		n1 = com_par['first']+ i * com_par['avg_bin']
		n2 = n1 + com_par['avg_bin']
		for j in xrange(n1,n2):
			avg.add_image(EMData(in_movie,j))
		avg.finish().write_image(ld_movie,i)			
	# lowdose sum
	avg=Averagers.get("mean")
	for i in xrange(n):
		avg.add_image(EMData(ld_movie,i))
	avg.finish().write_image(ld_sum)	
	
def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <movies>
	Output unfiltered fulldose sum (for ctf), filtered fulldose/lowdose sum, filtered lowdose averaged movies.
	Needs:
	Unblur (v1.0.2, Grant & Grigorieff, 2015)
	EMAN2 (v2.11, Tang et al., 2007)
	"""
	
	args_def = {'apix':1.25, 'voltage':200, 'time':200, 'rate':4, 'save':'0 0 0', 'save2':'0 0 0', 'xsuper':7420, 'delete':0}	
	parser = argparse.ArgumentParser()
	parser.add_argument("movie", nargs='*', help="specify movies to be processed")
	parser.add_argument("-a", "--apix", type=float, help="specify apix, by default {}".format(args_def['apix']))
	parser.add_argument("-v", "--voltage", type=int, help="specify the voltage (kV), by default {}".format(args_def['voltage']))
	parser.add_argument("-t", "--time", type=float, help="specify exposure time per frame in ms, by default {}".format(args_def['time']))
	parser.add_argument("-r", "--rate", type=float, help="specify dose rate in e/pix/s (counting pixel, not superresolution), by default {}".format(args_def['rate']))
	parser.add_argument("-s", "--save", type=str, help="save a specified number of aligned frames, by default {}, which means do not save. e.g., '0 19 4' means the saved movie starts from frame #0, ends at #19, in total (19-0+1)/4 = 5 frames. if 19 >= the real number of frames of the movie, skip".format(args_def['save']))
	parser.add_argument("-s2", "--save2", type=str, help="save a second specified number of aligned frames, by default {}, which means do not save. e.g., '0 31 4' means the saved movie starts from frame #0, ends at #19, in total (31-0+1)/4 = 8 frames. if 31 >= the real number of frames of the movie, skip".format(args_def['save2']))
	parser.add_argument("-x", "--xsuper", type=int, help="specify the x dimension of superresolution images, by default {}".format(args_def['xsuper']))
	parser.add_argument("-d", "--delete", type=int, help="delete (!!!) the raw movie (specify as 1), by default {}, which means do not delete".format(args_def['delete']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options"
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# get common parameters
	dose = str(args.time/1000.0 * args.rate / args.apix ** 2)
	apix = str(args.apix)
	voltage = str(args.voltage)
	com_par = {'dose':dose, 'apix':apix, 'voltage':voltage, 'save':args.save}
	# loop over all the input movies
	for movie in args.movie:
		movie_raw = movie
		basename = os.path.basename(os.path.splitext(movie)[0])
		basename_raw = basename
		# unify mrc format to mrcs format
		if movie[-4:] == '.mrc':
			m_link = basename+'.p3.mrcs'
			os.symlink(movie, m_link)
			movie, basename = file_base(m_link)			
		# get nimg
		com_par['nimg'] = EMUtil.get_image_count(movie)
		# unify the superresolution to counting	
		d=EMData(movie,0)
		if d["nx"] == args.xsuper:
			m_bin = basename+'_2x.p3.mrcs'
			for i in xrange(com_par['nimg']):
				d=EMData(movie, i)
				d.process_inplace("math.fft.resample",{"n":2})
				d.write_image(m_bin, i)
			movie, basename = file_base(m_bin)
		# unify counting dm4 format to mrcs format
		if movie[-4:] == '.dm4':
			m_mrcs = basename+'.p3.mrcs'
			for i in xrange(com_par['nimg']):
				d=EMData(movie, i)
				d.write_image(m_mrcs, i)
			movie, basename = file_base(m_mrcs)
		# link mrcs as mrc format
		in_movie = basename + '.p3.mrc'
		os.symlink(movie, in_movie)
		# unblur step 1: align frames, root = 'unfil'
		# unblur step 2: apply dose filter, root = 'fulldose'
		out_movie = run_unblur(run_unblur(in_movie, 'unfil', com_par), 'fulldose', com_par)
		# get lowdose
		first, last, avg_bin = args.save.split()
		com_par['first'], com_par['last'], com_par['avg_bin'] = int(first), int(last), int(avg_bin)
		if args.save != '0 0 0' and com_par['last'] < com_par['nimg']:
			in_movie = out_movie.replace('.mrc', '.mrcs')
			os.symlink(out_movie, in_movie)			
			get_ld(in_movie, 'lowdose', com_par)
			if args.save2 != '0 0 0':
				first, last, avg_bin = args.save2.split()
				com_par['first'], com_par['last'], com_par['avg_bin'] = int(first), int(last), int(avg_bin)
				if com_par['last'] < com_par['nimg']:
					get_ld(in_movie, 'lowdose2', com_par)
		# delete intermediate files, they contain '.p3.'
		for i in glob.glob(basename_raw + '*.p3.*'):
			os.unlink(i)
		# delete the raw movie!!!
		if args.delete == 1:
			os.unlink(movie_raw)
				
if __name__ == '__main__':
	main()
