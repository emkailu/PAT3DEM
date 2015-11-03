#!/usr/bin/env python

import os
import sys
import argparse
import pat3dem.star as p3s

def getkey(item):
	return float(item.split()[4])

def lines_group(lines_new, lines, group_num, new):
	if new == 1:
		group_num += 1
	for line in lines:
		line = line.split()
		line += ['group_{:05}'.format(group_num), '{:05}'.format(group_num)]
		lines_new += [' '.join(line) + '\n']
	return lines_new, group_num

def star_group(star, group):
	# calculate the number of particles in each micrograph
	star_dict = p3s.star_parse(star, 'data_')
	header_len = len(star_dict['data_'])+len(star_dict['loop_'])
	num_dict = {}
	with open(star) as read_star:
		lines = read_star.readlines()[header_len:-1]
		for line in lines:
			MicrographName = line.split()[0]
			num_dict[MicrographName] = num_dict.get(MicrographName, 0) + 1
	# sort by defocusU
	lines = sorted(lines, key=getkey)
	# group, if less than args.group, and transfer to lines_new
	lines_new = []
	group_num = 0
	while len(lines) > 0:
		MicrographName = lines[0].split()[0]
		num = num_dict[MicrographName]
		if num >= group:
			# check if already reach the end
			len_lines = len(lines)
			if num == len_lines:
				# new group
				lines_new, group_num = lines_group(lines_new, lines, group_num, 1)
				break
			for good, line_good in enumerate(lines):
				if line_good.split()[0] != MicrographName:break
			# new group
			lines_new, group_num = lines_group(lines_new, lines[:good], group_num, 1)
			lines = lines[good:]
		else:
			i = 0
			sets = set()			
			while num < group:
				for line in lines[:i+1]:
					MicrographName2 = line.split()[0]
					sets.add(MicrographName2)
				num = 0
				for micrograph in sets:
					num += num_dict[micrograph]
				if i < len(lines)-1:
					i += 1
					end = 0
				else:
					end = 1
					break
			if end == 0:
				for j, line2 in enumerate(lines[i:]):
					if line2.split()[0] != MicrographName2:break
				# new group
				lines_new, group_num = lines_group(lines_new, lines[:i+j], group_num, 1)
				lines = lines[i+j:]
				print 'Grouping {} into group_{:05}!\n'.format(sets, group_num)				
			if end == 1:
				# not new group
				lines_new, group_num = lines_group(lines_new, lines, group_num, 0)
				print 'Particles in {} cannot add up to more than {}, so they were grouped to the previous group: group_{:05}!\n'.format(sets, group, group_num)
				break
	return lines_new

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <star files>
	merge star files (including grouping), need:
	"""
	
	args_def = {'group':50, 'root':'zz'}
	parser = argparse.ArgumentParser()
	parser.add_argument("star", nargs='*', help="specify star files to be merged")
	parser.add_argument("-g", "--group", type=int, help="specify the minimal number of particles for one group, by default {}".format(args_def['group']))
	parser.add_argument("-r", "--root", help="specify rootname for output, by default '{}'".format(args_def['root']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options"
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# 
	merged = args.root + '_merged.star'
	write_merge = open(merged, 'w')
	header = '\ndata_\n\nloop_ \n_rlnMicrographName #1 \n_rlnCoordinateX #2 \n_rlnCoordinateY #3 \n_rlnImageName #4 \n_rlnDefocusU #5 \n_rlnDefocusV #6 \n_rlnDefocusAngle #7 \n_rlnVoltage #8 \n_rlnSphericalAberration #9 \n_rlnAmplitudeContrast #10 \n_rlnMagnification #11 \n_rlnDetectorPixelSize #12 \n_rlnCtfFigureOfMerit #13 \n'
	write_merge.write(header)
	for star in args.star:
		star_dict = p3s.star_parse(star, 'data_')
		header_len = len(star_dict['data_'])+len(star_dict['loop_'])
		with open(star) as read_star:
			for line in read_star.readlines()[header_len:-1]:
				l = line.split()
				line_new = l[star_dict['_rlnMicrographName']], l[star_dict['_rlnCoordinateX']], l[star_dict['_rlnCoordinateY']], l[star_dict['_rlnImageName']], l[star_dict['_rlnDefocusU']], l[star_dict['_rlnDefocusV']], l[star_dict['_rlnDefocusAngle']], l[star_dict['_rlnVoltage']], l[star_dict['_rlnSphericalAberration']], l[star_dict['_rlnAmplitudeContrast']], l[star_dict['_rlnMagnification']], l[star_dict['_rlnDetectorPixelSize']], l[star_dict['_rlnCtfFigureOfMerit']] + ' \n'
				write_merge.write(' '.join(line_new))
	write_merge.write(' \n')	
	write_merge.close()
	print 'The merged star has been written in {}!\n'.format(merged)
	grouped = args.root + '_merged_grouped.star'
	with open(grouped, 'w') as write_group:
		write_group.write(header)
		write_group.write('_rlnGroupName #14 \n_rlnGroupNumber #15 \n')
		write_group.write(''.join(star_group(merged, args.group)))
		write_group.write(' \n')
	print 'The grouped star has been written in {}!\n'.format(grouped)
	
if __name__ == '__main__':
	main()
