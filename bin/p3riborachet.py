#!/usr/bin/env python

import os
import sys
import argparse
import pat3dem.star as p3s
import scipy.optimize as opt
from EMAN2 import EMData, Transform
#from sparx import generate_ctf, filt_ctf

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <mrc>
	Use one 2D image to derive the conformation of a flexible complex consisting of mutiple rigid-body domains.
	"""
	
	args_def = {'apix':1, 'star':'data.star', 'res':10}	
	parser = argparse.ArgumentParser()
	parser.add_argument("mrc", nargs='*', help="specify mrc for the rigid-body domains")
	parser.add_argument("-a", "--apix", type=float, help="specify the apix, by default {}".format(args_def['apix']))
	parser.add_argument("-s", "--star", type=str, help="specify the star file and put the particles in the corresponding folder, by default {}".format(args_def['star']))
	parser.add_argument("-r", "--res", type=float, help="specify the resolution, by default {}".format(args_def['res']))
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
	c_p = {'m':args.mrc, 'star':args.star}
	# loop through particle by star file
	star_dict = p3s.star_parse(c_p['star'], 'data_')
	header_len = len(star_dict['data_'])+len(star_dict['loop_'])
	with open(c_p['star']) as s_read:
		lines = s_read.readlines()[header_len:-1]
	for line in lines:
		line = line.split()
		num, rlnImageName = line[star_dict['_rlnImageName']].split('@')
		print num, rlnImageName
		#c_p['ptcl'] = EMData(rlnImageName, int(num)-1)
		c_p['ptcl'] = EMData('70S-half1_30spin_-2.mrc')
		#c_p['ptcl-lp10'] = c_p['ptcl'].process("filter.lowpass.gauss", {"apix":args.apix, "cutoff_freq":0.05})
		c_p['psi'] = star_dict['_rlnAnglePsi']
		c_p['theta'] = star_dict['_rlnAngleTilt']
		c_p['phi'] = star_dict['_rlnAngleRot']
		c_p['tx'] = -star_dict['_rlnOriginX']
		c_p['ty'] = -star_dict['_rlnOriginY']
		minimize(c_p)
			
def minimize(c_p):
	# brute force
	f = lambda x: ccc(x, c_p)
	rranges = [slice(-10, 10, 1)]
	c_p['c'] = 3 # store global minima
	resbrute = opt.brute(f, rranges, full_output=True, finish=opt.fmin)
	
def ccc(x, c_p):
	x = float(x)
	m0 = c_p['m'][0]
	m = c_p['m'][1]
	e=EMData(m)
	e.transform(Transform({'n1':1,'n2':1,'n3':1, 'omega':x, 'tx':0.00,'ty':0.00,'tz':0.00,'mirror':0,'scale':1.0000,'type':'spin'}))
	# add together
	avg = EMData(m0)
	avg.add(e)
	# project
	t = {'psi':c_p['psi'],'theta':c_p['theta'],'phi':c_p['phi'],'tx':c_p['tx'],'ty':c_p['ty'],'type':'spider'}
	t2 = {'psi':0,'theta':0,'phi':0,'tx':0,'ty':0,'type':'spider'}
	proj = avg.project("standard", Transform(t2))
	'''
	ctf = generate_ctf([2.16784296875000000000, 2, 200, 1.25, 0, 10, 0.00841601570000000000,20.597069])
	ctf_proj = filt_ctf(proj, ctf)
	'''
	#c = proj.cmp("ccc",c_p['ptcl-lp10'], {"mask":EMData("mymask.hdf")})
	#proj.process_inplace("normalize.edgemean")
	c_p['ptcl']=c_p['ptcl']
	c = proj.cmp("optsub",c_p['ptcl'], {"maxres":80.0})
	print x,c
	if c < c_p['c']:
		#print c,x
		c_p['c'] = c
		#proj.write_image('zz.mrc')
	return c

if __name__ == '__main__':
	main()