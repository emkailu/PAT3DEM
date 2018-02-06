#!/usr/bin/env python

import os
import sys
import math
import argparse
import subprocess
import numpy as np
import pat3dem.pdb as p3p
import scipy.optimize as opt
from EMAN2 import *

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <pdbs>
	Use one 2D image to derive the conformation of a flexible complex consisting of mutiple rigid-body domains.
	"""
	
	args_def = {'apix':1, 'ptcl':'ptcl.mrc', 'res':10}	
	parser = argparse.ArgumentParser()
	parser.add_argument("pdb", nargs='*', help="specify pdbs for the rigid-body domains")
	parser.add_argument("-a", "--apix", type=float, help="specify the apix, by default {}".format(args_def['apix']))
	parser.add_argument("-p", "--ptcl", type=str, help="specify the particle, by default {}".format(args_def['ptcl']))
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
	c_p = {'ptcl':EMData(args.ptcl)}
	c_p['box'] = c_p['ptcl']["nx"]
	# store the maps generated from pdbs
	c_p['m'] = []
	for pdb in args.pdb:
		mrc = p3p.pdb2mrc(pdb,args.apix,args.res,False,c_p['box'],None,True)
		c_p['m'] += [mrc]
	minimize2(c_p)
			
def minimize(c_p):
	# brute force
	f = lambda x: ccc(x, c_p)
	b, n = c_p['box']/2, len(c_p['m'])
	rranges = [slice(0, 360, 30), slice(0, 180, 15), slice(0, 360, 30), slice(-b, b, b/2), slice(-b, b, b/2), slice(-b, b, b/2)] * n
	c_p['c'] = 3 # store global minima
	res = opt.brute(f, rranges, full_output=True, finish=opt.fmin)
	
class RandomDisplacementBounds(object):
	"""random displacement with bounds"""
	def __init__(self, xmin, xmax, stepsize=10):
		self.xmin = xmin
		self.xmax = xmax
		self.stepsize = stepsize
    
	def __call__(self, x):
		"""take a random step but ensure the new position is within the bounds"""
		while True:
		    # this could be done in a much more clever way, but it will work for example purposes
			xnew = x + np.random.uniform(-self.stepsize, self.stepsize, np.shape(x))
			if np.all(xnew < self.xmax) and np.all(xnew > self.xmin):
				break
		return xnew
	
def minimize2(c_p):
	#basinhopping
	f = lambda x: ccc(x, c_p)
	b, n = c_p['box']/2, len(c_p['m'])
	# the starting point
	x0 = [0, 0, 0, 0, 0, 0] * n
	# the bounds
	xmin = [0, 0, 0, -b, -b, -b]*n
	xmax = [360, 360, 360, b, b, b]*n
	# rewrite the bounds in the way required by L-BFGS-B
	bounds = [(low, high) for low, high in zip(xmin, xmax)]
	# use method L-BFGS-B because the problem is smooth and bounded
	minimizer_kwargs = dict(method="L-BFGS-B", bounds=bounds)
	# define the new step taking routine and pass it to basinhopping
	take_step = RandomDisplacementBounds(xmin, xmax)	
	c_p['c'] = 3 # store global minima
	res = opt.basinhopping(f, x0, minimizer_kwargs=minimizer_kwargs, take_step=take_step, niter=10000)	
	
def ccc(x, c_p):
	avg=Averagers.get("mean")
	for i, m in enumerate(c_p['m']):
		j = 6*i
		t = {'az':x[j],'alt':x[j+1],'phi':x[j+2],'tx':x[j+3],'ty':x[j+4],'tz':x[j+5],'mirror':0,'scale':1.0000,'type':'eman'}
		avg.add_image(m.project("standard", Transform(t)))
	avg = avg.finish()
	c = avg.cmp("ccc",c_p['ptcl'])
	if c < c_p['c']:
		print c
		print x	
		c_p['c'] = c
		avg.write_image('zz.mrc')
	return c

if __name__ == '__main__':
	main()