#!/usr/bin/env python

import os
import sys
import argparse
import pat3dem.star as p3s

def s2i(x):
	return int(float(x))

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <local.star>
	Use the input local CTF UVA to replace a star file.
	"""
	
	args_def = {'star':''}	
	parser = argparse.ArgumentParser()
	parser.add_argument("local", nargs='*', help="specify *local.star files")
	parser.add_argument("-s", "--star", type=str, help="specify the star file to be replaced, by default {}. The matching between local.star and to-be-replaced star will only be based on _rlnMicrographName, _rlnCoordinateX and _rlnCoordinateY. It also works for movie star if '_movie.mrcs' is the movie stack of '.mrc'.".format(args_def['star']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# get info of the to-be-replaced star file
	star = args.star
	star_dict = p3s.star_parse(star, 'data_')
	mic0, x0, y0, u0, v0, a0 = star_dict['_rlnMicrographName'], star_dict['_rlnCoordinateX'], star_dict['_rlnCoordinateY'], star_dict['_rlnDefocusU'], star_dict['_rlnDefocusV'], star_dict['_rlnDefocusAngle']
	header = star_dict['data_'] + star_dict['loop_']
	header_len = len(header)
	with open(star) as star_read:
		lines = star_read.readlines()[header_len:-1]
	lines = [line.split() for line in lines]
	# create a dict to index the lengthy lines
	line_num = {}
	for i,line in enumerate(lines):
		lmic0 = line[mic0].split('@')[-1].replace('_movie.mrcs','').replace('.mrc','')# may be movie star
		k = (lmic0,s2i(line[x0]),s2i(line[y0]))
		line_num[k] = line_num.get(k, []) + [i]
	# get some info about the local.star
	s = args.local[0]
	sd = p3s.star_parse(s, 'data_')
	mic, x, y, u, v, a = sd['_rlnMicrographName'], sd['_rlnCoordinateX'], sd['_rlnCoordinateY'], sd['_rlnDefocusU'], sd['_rlnDefocusV'], sd['_rlnDefocusAngle']
	h = sd['data_'] + sd['loop_']
	hl = len(h)
	# loop through all the local.star files
	j = 0
	for s in args.local:
		with open(s) as read_s:
			ls = read_s.readlines()[hl:] # the last line is not empty for local.star
		# loop through all the lines in each local.star file
		for l in ls:
			l = l.split()
			lmic = l[mic].replace('.mrc','')
			k = (lmic,s2i(l[x]), s2i(l[y]))
			for ind in line_num[k]:
				lines[ind][u0],lines[ind][v0],lines[ind][a0] = l[u], l[v], l[a]
				j+=1
				print 'Replacing line {}. Replaced {} lines.'.format(ind, j)
	# start a new file
	basename = os.path.basename(os.path.splitext(star)[0])
	uva = '{}-local.star'.format(basename)
	with open(uva, 'w') as uva_w:
		uva_w.write(''.join(header))
		for line in lines:
			uva_w.write(' '.join(line)+'\n')
		uva_w.write('\n')
		
if __name__ == '__main__':
	main()
