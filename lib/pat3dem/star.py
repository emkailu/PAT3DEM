#!/usr/bin/env python

# Assumption for the star format:
# contain one or more 'data_*' blocks, for each block, 
# either
'''

data_*

loop_
item1 #1
...
itemn #n
item1_data ... itemn_data
...
item1_data ... itemn_data

'''
# or
'''

data_*

item1 item1_data
...
itemn itemn_data

'''

def star_data(star):
	# return 2 dict: {data1:line_num, data2:line_num}, {data1:lines, data2:lines}
	data_dict = {}
	with open(star) as read:
		for i, line in enumerate(read.readlines()):
			if line[:5] == 'data_':
				line = line.strip()
				data_dict[line] = i
	# get an inverse dictionary
	inv = {v: k for k, v in data_dict.items()}
	# get the lines for each key
	d_lines_dict = {}
	with open(star) as read:
		lines = read.readlines()
		line_num = sorted(inv)
		for i, num in enumerate(line_num):
			try:
				newline = line_num[i+1]
			except IndexError:
				newline = len(lines) + 1
			d_lines_dict[inv[num]] = lines[num-1:newline-1]
	return data_dict, d_lines_dict

def data_parse(d_lines):
	# return a dict, whose keys are 'data_', ('loop_'), and items in 'data_'/'loop_'
	item_dict = {}
	if d_lines[3][:5] == 'loop_':
		n = 4
	else:
		n = 3
	item_dict['data_'] = d_lines[:n]
	for i, line in enumerate(d_lines[n:]):
		if line[:4] != '_rln': break
	item_dict['loop_'] = d_lines[n:n+i]
	for j in item_dict['loop_']:
		k, v = j.split()
		# change the value to an integer and minus 1, to be convenient
		if n == 4:
			item_dict[k] = int(v.strip('#')) - 1
		elif n == 3:
			item_dict[k] = v.strip()
	return item_dict

def star_parse(star, data):
	# parse a star file containing the data label.
	# return a dict, whose keys are 'data_', ('loop_'), and items in 'data_'/'loop_'
	d_lines = star_data(star)[1][data]
	return data_parse(d_lines)
