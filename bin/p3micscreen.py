#!/usr/bin/env python

import os
import sys
import argparse
import numpy
import math

def eval_unblur(root):
	# return the unblur score
	with open(root.replace('_fulldose', '_unblur.log')) as read:
		line = read.readlines()[-5]
	        if line[:11] != 'Final Score':
			sys.exit('Error: can not find unblur score!')
	return float(line.split()[-1])

def eval_ctffind(root):
	# return defocus and best Thon rings
	with open(root+'.txt') as read:
		line = read.readlines()[-1].split()
	return float(line[1]), float(line[-1])

def eval_coord(root):
	# return number of ptcls
	coord = root+'.box'
	if not os.path.isfile(coord):
		coord = root+'.star'
	with open(coord) as read:
		nump = len(read.readlines())
	return nump		

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <micrographs>
	screen micrographs based on outputs of p3movie.py and p3ctf.py, modulated by numptcl and defocus
	"""
	
	args_def = {'weight':'1 1'}	
	parser = argparse.ArgumentParser()
	parser.add_argument("mic", nargs='*', help="specify micrographs (in mrc format) to be screened")
	parser.add_argument("-w", "--weight", type=str, help="specify weights, by default '{}', which means sig = sig(unblur/sqrt(nump)/defocus) * 1 + sig(1/thon/sqrt(nump)) * 1, use 0 to ignore one of them".format(args_def['weight']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options"
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# loop over the input micrographs, get a dictionary {mic:[score1, score2]}
	score_dict = {}
	for mic in args.mic:
		root = mic[:-4]
		unblur = eval_unblur(root)
		defoc, thon = eval_ctffind(root)
		nump = math.sqrt(eval_coord(root))			
		score_dict[mic] = [unblur / nump / defoc, 1 / thon / nump]
	# calculate statistics in an array
	arr = numpy.array(score_dict.values())
	mean, sig = numpy.mean(arr, axis=0), numpy.std(arr, axis=0)
	unblur_m, thon_m = mean
	unblur_sig, thon_sig = sig
	# get a sigma dictionary {mic:[sig_unblur, sig_thon]}
	sig_dict = {}
	for mic in args.mic:
		unblur_sc, thon_sc = score_dict[mic]
		sig_dict[mic] = [(unblur_sc-unblur_m)/unblur_sig, (thon_sc-thon_m)/thon_sig]		
	# get a weighted sigma dictionary {mic:sig_unblur*w1,sig_thon*w2}
	w1, w2 = args.weight.split()
	w1, w2 = float(w1), float(w2)		
	sigw_dict = {}
	for mic in args.mic:
		mic_u_sig, mic_t_sig = sig_dict[mic]
		sigw_dict[mic] = mic_u_sig * w1 + mic_t_sig * w2
	# get an inverse dictionary
	inv = {}
	for k, v in sigw_dict.iteritems():
		inv[v] = inv.get(v, []) + [k]
	for i in sorted(inv, reverse=True):
		print i, ['{} [unblur_sig, Thon_sig]: {}'.format(mic, sig_dict[mic]) for mic in inv[i]]	
			
if __name__ == '__main__':
	main()
