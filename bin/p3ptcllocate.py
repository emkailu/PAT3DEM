#!/usr/bin/env python

import os
import sys
import argparse
from EMAN2 import *

def ptclCorr(d, com_par):
	# This function will return best correlation map (peak values)
	num = EMUtil.get_image_count(com_par['refs'])
	for i in xrange(num):
		ref = EMData(com_par['refs'], i)
		ccfmap = d.calc_ccf(ref)
		ccfmap.process_inplace("mask.onlypeaks",{"npeaks":0})
		ccfmap.write_image('tt.mrc')
		threshold=ccfmap["sigma"]*2.5
		peaks=ccfmap.calc_highest_locations(threshold)
	return peaks

def boxesFrom(d, peaks, com_par):
	boxes = []
	rs = com_par['rs']
	for i in peaks:
		clip = d.get_clip(Region(i.x-rs/2, i.y-rs/2, rs, rs))
		ref = EMData(com_par['refs'],0)
		ref.process_inplace("normalize.toimage",{"to":clip})
		clip.sub(ref)
		if fabs(clip["kurtosis"])>com_par['thr3'] or clip["skewness"]<com_par['thr2'] or clip["sigma"]>com_par['thr1'] or clip["skewness"]==1:
			continue
		boxes += [(i.x, i.y)]
	return boxes

def write_box(boxes, image, com_par):
	basename = os.path.basename(os.path.splitext(image)[0])
	rs = com_par['rs']
	with open(basename+'.box', 'w') as w_box:
		for i in boxes:
			w_box.write('{}\t{}\t{}\t{}\n'.format(i[0]-rs/2, i[1]-rs/2, rs, rs))

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <image.mrc>
	Locate particles in image.mrc. (basically a Python version of EMAN1.9 batchboxer.C)
	Needs:
	EMAN2 (v2.12, Tang et al., 2007)
	"""
	
	args_def = {'threshold':'1 1 1', 'reference':'0'}	
	parser = argparse.ArgumentParser()
	parser.add_argument("image", nargs='*', help="specify images to be processed")
	parser.add_argument("-t", "--threshold", type=str, help="specify thresholds, by default {}".format(args_def['threshold']))
	parser.add_argument("-r", "--reference", type=str, help="specify references, by default {}".format(args_def['reference']))
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
	thr = args.threshold.split()
	com_par = {'thr1':float(thr[0]), 'thr2':float(thr[1]), 'thr3':float(thr[2]), 'refs':args.reference}
	ref = EMData(com_par['refs'], 0)
	com_par['rs'] = ref["nx"]
	# loop over all the input images
	for image in args.image:
		d = EMData(image, 0)
		d.process_inplace("normalize")
		write_box(boxesFrom(d, ptclCorr(d, com_par), com_par), image, com_par)
				
if __name__ == '__main__':
	main()
