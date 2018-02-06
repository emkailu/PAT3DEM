#!/usr/bin/env python

import os
import sys
import argparse
import pat3dem.star as p3s
import copy

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <data.star>
	Output a star file for 'relion_particle_polish (Relion v1.4)', based on the data.star of refined Dose-Weighted particles. No rotation or translation.
	"""
	
	args_def = {'num':38, 'rootDW':'_DW', 'rootm':'_movie', 'rootc':'_centered_checked'}	
	parser = argparse.ArgumentParser()
	parser.add_argument("star", nargs='*', help="specify data.star of the refined Dose-Weighted particles")
	parser.add_argument("-n", "--num", type=int, help="specify number of frames in one movie, by default {}".format(args_def['num']))
	parser.add_argument("-rd", "--rootDW", type=str, help="specify root name of Dose-Weighting, by default {}".format(args_def['rootDW']))
	parser.add_argument("-rm", "--rootm", type=str, help="specify root name of movies, by default {}".format(args_def['rootm']))
	parser.add_argument("-rc", "--rootc", type=str, help="specify root name of coord files, by default {}. The files location must stay the same as in the particle extraction step".format(args_def['rootc']))
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
	star = args.star[0]
	s_d = p3s.star_parse(star, 'data_')
	header = s_d['data_'] + s_d['loop_']
	header_len = len(header)
	with open(star) as star_read:
		lines = star_read.readlines()[header_len:-1]
	lines = [line.split() for line in lines]
	lines = sorted(lines, key= lambda x: (x[s_d['_rlnMicrographName']],x[s_d['_rlnImageName']].split('@')[0])) # sort by mic first and then particle number
	# add more tags
	s_d_count = copy.deepcopy(s_d)
	del s_d_count['data_'],s_d_count['loop_']
	m = max(s_d_count.values()) + 1
	for i,tag in enumerate(['_rlnAngleRotPrior','_rlnAngleTiltPrior','_rlnAnglePsiPrior','_rlnOriginXPrior','_rlnOriginYPrior','_rlnNrOfFrames','_rlnOriginalParticleName']):
		s_d[tag] = m+i
		s_d['loop_'].append(tag+' #{} \n'.format(m+i+1))
	# start a new file
	basename = os.path.basename(os.path.splitext(star)[0])
	polish = '{}-for-polish.star'.format(basename)
	with open(polish, 'w') as polish_w:
		# header first
		# change data_ to data_images
		s_d['data_'] = ['data_images\n' if x=='data_\n' else x for x in s_d['data_']]
		s_d['data_images'] = s_d.pop('data_')
		if '_rlnGroupName' not in s_d:
			# change _rlnGroupNumber to _rlnGroupName
			s_d['loop_'] = ['_rlnGroupName #{} \n'.format(s_d['_rlnGroupNumber']+1) if x=='_rlnGroupNumber #{} \n'.format(s_d['_rlnGroupNumber']+1) else x for x in s_d['loop_']]
			s_d['_rlnGroupName'] = s_d.pop['_rlnGroupNumber']
		else:
			s_d2 = copy.deepcopy(s_d)
			s_d2.pop['_rlnGroupNumber']
			print "bug here"
		header = s_d2['data_images'] + s_d2['loop_']
		polish_w.write(''.join(header))
		# main body
		for i,line in enumerate(lines):
			# add 7 in order
			line.append(line[s_d['_rlnAngleRot']])
			line.append(line[s_d['_rlnAngleTilt']])
			line.append(line[s_d['_rlnAnglePsi']])
			line.append(line[s_d['_rlnOriginX']])
			line.append(line[s_d['_rlnOriginY']])
			line.append(str(args.num))
			line.append(line[s_d['_rlnImageName']].replace(args.rootDW,''))
			# change the following 3
			line[s_d['_rlnGroupName']] = 'group_{}'.format(line[s_d['_rlnGroupName']])
			with open(line[s_d['_rlnMicrographName']].replace(args.rootDW+'.mrc',args.rootc+'.star')) as coord_r:
				PtclLines = coord_r.readlines()
			PtclTotal = len(PtclLines) - 7
			MicrographName = line[s_d['_rlnMicrographName']].replace(args.rootDW+'.mrc',args.rootm+'.mrcs')
			PtclIndex, ImageName = line[s_d['_rlnImageName']].replace(args.rootDW+'_',args.rootm+'_').split('@')
			for j in xrange(args.num):
				line[s_d['_rlnMicrographName']] = '{:06d}@{}'.format(j+1, MicrographName)
				line[s_d['_rlnImageName']] = '{:06d}@{}'.format(int(PtclIndex) + j*PtclTotal, ImageName)
				polish_w.write(' '.join(line)+'\n')
		polish_w.write('\n')
				
if __name__ == '__main__':
	main()
