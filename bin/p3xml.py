#!/usr/bin/env python

import os
import sys
import argparse
import xml.etree.ElementTree as XE
from EMAN2 import *
from emimage import EMWidgetFromFile
from emapplication import EMApp

def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <xml>
	Convert xml to txt and optionally display them
	"""
	
	args_def = {'display':1}	
	parser = argparse.ArgumentParser()
	parser.add_argument("xml", nargs='*', help="specify xml files to be processed")
	parser.add_argument("-d", "--display", type=int, help="disply (1) or not (0), by default {}".format(args_def['display']))
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
	for xml in args.xml:
		with open(xml+'.txt', 'w') as w_txt:
			for coord in XE.parse(xml).getroot():
				for xy in coord:
					if xy.tag == 'x':
						w_txt.write(xy.text + '\t')
					else:
						w_txt.write(xy.text + '\n')
	# display
	if args.display == 1:
		app = EMApp()
		for xml in args.xml:
			filename = xml+'.txt'
			w = EMWidgetFromFile(filename,application=app,force_2d=False)
			w.setWindowTitle(base_name(filename))
			app.show_specific(w)
		app.exec_()			
				
if __name__ == '__main__':
	main()
