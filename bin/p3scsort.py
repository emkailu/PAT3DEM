#!/usr/bin/env python

import os
import sys
import argparse
import re

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <sc>
	Sort rosetta score files.
	"""
	
	args_def = {'sort':'0', 'save':-1, 'percent':20}	
	parser = argparse.ArgumentParser()
	parser.add_argument("sc", nargs='*', help="specify score files to be sorted")
	parser.add_argument("-s", "--sort", type=str, help="specify a sorting method, by default {}. e.g., '0-2' means column 0 subtract column 2".format(args_def['sort']))
	parser.add_argument("-sv", "--save", type=int, help="specify save, by default {}. e.g., -1 means save column -1".format(args_def['save']))
	parser.add_argument("-p", "--percent", type=float, help="specify percent, by default {}. e.g., 20 means save 20 percent".format(args_def['percent']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# interpret sorting methods
	sm = args.sort
	sm += '*1' # tricky
	num = re.split('\+|\-|\*|\/', sm)
	clm = []
	for i in num:
		clm += ['c[{}]'.format(i)] # for a direct use of eval()
	opr = []
	for i in re.split('[0-9]', sm):
		if i != '':
			opr += [i]
	sm = ''.join([j for i in zip(clm, opr) for j in i][:-1]) # a tricky method to merge strings
	print 'Your sorting method is {}.'.format(sm)
	# loop over score files
	scores = {}
	for i in args.sc:
		with open(i) as read_sc:
			lines = read_sc.readlines()
		for line in lines:
			l = line.split()
			if len(l) > 1 and 'total_score' not in line:
				c = []
				for j in l:
					try:
						c += [float(j)]
					except ValueError:
						c += [j]
				scores[line] = eval(sm)
	# get an inverse dictionary
	inv = {}
	for k, v in scores.iteritems():
		inv[v] = inv.get(v, []) + [k]
	sort = ''
	for i in sorted(inv):
		sort += ''.join(inv[i])
	print sort
	sort = sort.split('\n')
	with open('zz{}.txt'.format(args.sort), 'w') as out:
		cut = int(args.percent / 100.0 * len(scores))
		for i in xrange(cut):
			out.write(sort[i].split()[args.save]+'\n')
			
if __name__ == '__main__':
	main()
