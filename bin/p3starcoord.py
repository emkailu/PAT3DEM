#!/usr/bin/env python

import os
import sys
import argparse
import pat3dem.star as p3s

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <star files>
	Output the coordinates from the star files.
	"""
	
	args_def = {'box':-1, 'edge':-1, 'x':3710, 'y':3838}	
	parser = argparse.ArgumentParser()
	parser.add_argument("star", nargs='*', help="specify star files to be processed")
	parser.add_argument("-b", "--box", type=int, help="specify a box size (in pixel) for output, by default {}, which means the output will be .star format only and no .box output".format(args_def['box']))
	parser.add_argument("-e", "--edge", type=int, help="specify a minimal distance (in pixel) between center of boxes and edge of micrographs, by default {}, which means all coordinates will be output".format(args_def['edge']))
	parser.add_argument("-x", "--x", type=int, help="provide the x dimension (in pixel) of micrographs, by default {}".format(args_def['x']))
	parser.add_argument("-y", "--y", type=int, help="provide the y dimension (in pixel) of micrographs, by default {}".format(args_def['y']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options"
		sys.exit(1)	
	else:
		# get default values
		for i in args_def:
			if args.__dict__[i] == None:
				args.__dict__[i] = args_def[i]
		# loop over all the input files		
		for i in args.star:
			star_dict = p3s.star_parse(i, 'data_')
			header_len = len(star_dict['data_'])+len(star_dict['loop_'])
			if '_rlnImageName' in star_dict:
				out_dict = {}
				with open(i) as s_read:
					lines = s_read.readlines()[header_len:-1]
					# loop over lines, generate a dict: {out_name:[{ptcl#:line#}]}
					for j, line in enumerate(lines):
						line = line.split()
						num, rlnImageName = line[star_dict['_rlnImageName']].split('@')
						out_name = '_'.join(os.path.relpath(rlnImageName[:-5]).replace('\\','/').split('/'))
						out_dict[out_name] = out_dict.get(out_name, []) + [{num:j}]
					# loop over out_dict, write coords for each key
					for k in out_dict:
						out = k+'.star'
						if args.box != -1:
							out_box = k+'.box'
							o_box_write = open(out_box, 'a')
						with open(out, 'a') as o_write:
							o_write.write('\ndata_\n\nloop_ \n_rlnCoordinateX #1 \n_rlnCoordinateY #2 \n')
							for l in sorted(out_dict[k]):
								line = lines[l.values()[0]].split()
								# get old coord
								x, y = float(line[star_dict['_rlnCoordinateX']]), float(line[star_dict['_rlnCoordinateY']])
								# calculate new coord
								if '_rlnOriginX' in star_dict and '_rlnOriginY' in star_dict:
									x -= float(line[star_dict['_rlnOriginX']])
									y -= float(line[star_dict['_rlnOriginY']])
								# skip the edge
								if args.edge != -1:
									if not args.edge<=x<=args.x-args.edge or not args.edge<=y<=args.y-args.edge:
										continue
								o_write.write('{:>12} '.format(x) + '{:>12} \n'.format(y))
								if args.box != -1:
									o_box_write.write('{}'.format(x-args.box/2) + '\t{}'.format(y-args.box/2) + '\t{}'.format(args.box) * 2 + '\n')
							o_write.write('\n')
						if args.box != -1:
							o_box_write.close()
			elif args.box != -1:
				basename = os.path.basename(os.path.splitext(i)[0])
				with open(i) as s_read:
					lines = s_read.readlines()[header_len:-1]
					with open(basename+'.box', 'w') as o_box_write:
						for line in lines:
							line = line.split()
							# get old coord
							x, y = float(line[star_dict['_rlnCoordinateX']]), float(line[star_dict['_rlnCoordinateY']])
							# skip the edge
							if args.edge != -1:
								if not args.edge<=x<=args.x-args.edge or not args.edge<=y<=args.y-args.edge:
									continue
							o_box_write.write('{}'.format(x-args.box/2) + '\t{}'.format(y-args.box/2) + '\t{}'.format(args.box) * 2 + '\n')
				
if __name__ == '__main__':
	main()
