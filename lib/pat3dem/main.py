#!/usr/bin/env python

import os
import sys
from EMAN2 import *
import matplotlib.pyplot as plt

def driftcor_ctf_ptclpick(movie, cluster):
	# Submit a job to 'cluster', to do motioncor2, Gctf and Gautomatch all at once for 'movie'. The 'movie' may contain folder name.
	basename = os.path.basename(os.path.splitext(movie)[0])
	basename = os.path.basename(os.path.splitext(basename)[0]) # In case of .mrc.gz
	path = os.path.dirname(movie)
	template="""# p3motioncor2opt.py
{MOTIONCOR2OPT} {PROJECT_FOLDER}/rawmovies/{movie} -a {APIX} -ar {APIXR} -b {BIN} -p {PATCH} -v {VOLTAGE} -t {TIME} -r {RATE} -ta {TARGET} -ti '{TILT}' -g '{GAINREF}' -s {SAVE}

# move output to Micrographs/sub-sub-folder/
if fDW=$( ls ../../Micrographs/{path}/{basename}_throw???_DW.mrc ); then
	printf 'Have the motioncor2 output already been moved to Micrographs/? OK if yes!\\n'
else
	if fDW=$( ls {basename}_throw???_DW.mrc ); then
		mv $fDW ${{fDW/_DW./.}} ../../Micrographs/{path}/
	else
		printf 'Cannot find _DW.mrc, indicating a bad movie. No further processing!\\n'
	        exit 1
	fi
fi

# Gctf
cd {PROJECT_FOLDER}/Micrographs/{path}/; {GCTF} ${{fDW/_DW./.}} --apix {apix_final} --dstep {DSTEP} --kV {VOLTAGE} --cs {CS} --ac {AC} --do_EPA 1 --logsuffix _ctffind3.log --ctfstar NONE

# Rename Gctf output
if [ {GCTF_RENAME} = 'yes' ]; then
	fCTF=${{fDW/_DW.mrc/.ctf}}
	mv $fCTF ${{fCTF/.ctf/_DW.ctf}}
	mv ${{fCTF/.ctf/_ctffind3.log}} ${{fCTF/.ctf/_DW_ctffind3.log}}
fi

# Gautomatch
{GAUTOMATCH} $fDW --apixM {apix_final} --diameter {DIAMETER} --min_dist {MINDIST} --cc_cutoff {CC_CUTOFF}
"""
	context = {
	"MOTIONCOR2OPT":os.environ['MOTIONCOR2OPT'],
	"PROJECT_FOLDER":os.environ['PROJECT_FOLDER'],
	"APIX":os.environ['APIX'],
	"APIXR":os.environ['APIXR'],
	"BIN":os.environ['BIN'],
	"PATCH":os.environ['PATCH'],
	"VOLTAGE":os.environ['VOLTAGE'],
	"TIME":os.environ['TIME'],
	"RATE":os.environ['RATE'],
	"TARGET":os.environ['TARGET'],
	"TILT":os.environ['TILT'],
	"GAINREF":os.environ['GAINREF'],
	"SAVE":os.environ['SAVE'],
	"GCTF":os.environ['GCTF'],
	"DSTEP":os.environ['DSTEP'],
	"CS":os.environ['CS'],
	"AC":os.environ['AC'],
	"GCTF_RENAME":os.environ['GCTF_RENAME'],
	"GAUTOMATCH":os.environ['GAUTOMATCH'],
	"DIAMETER":os.environ['DIAMETER'],
	"MINDIST":os.environ['MINDIST'],
	"CC_CUTOFF":os.environ['CC_CUTOFF'],
	"movie":movie,
	"path":path,
	"basename":basename,
	"apix_final":float(os.environ['APIXR']) * float(os.environ['BIN'])
	 }
	fscript = "{}_p3.sh".format(basename)
	with open(fscript, 'w') as f:
		f.write(template.format(**context))
	print "Submitting the preprocessing job for {} ...".format(movie)
	import pat3dem.cluster as p3c
	getattr(p3c, cluster)(fscript, basename, 2, 1, 1, 1, 1, 20, 1)

def dwnld_driftcor_ctf_ptclpick(out, cluster):
	# Submit a job to monitor download and submit preprocessing jobs
	template = """printf 'Creating the sub-folders motioncor2/, Micrographs/, and sub-sub-folders ...\\n'
sbsbfd=()
while IFS='/' read -r col1 col2
do
    if ! echo "${{sbsbfd[@]}}" | grep -q -w "$col1"; then
        sbsbfd+=("$col1")
    fi
done <"{PROJECT_FOLDER}/rawmovies/f.txt"
unset IFS
for i in "${{sbsbfd[@]}}"
do
    for j in "motioncor2" "Micrographs"
    do
        mkdir -p "{PROJECT_FOLDER}/$j/$i"
    done
done
printf "Done!\\n\\n"

printf "Submit a preprocessing job if the downloading of a movie is complete.\\n"
read f <"{PROJECT_FOLDER}/rawmovies/f.txt"
while read fnew
do
    while [ ! -f "{PROJECT_FOLDER}/rawmovies/$fnew" ]
    do
        sleep 10s
    done
    if [ "$f" != "$fnew" ]; then
        IFS='/'; fsplit=($f); unset IFS
        cd "{PROJECT_FOLDER}/motioncor2/${{fsplit[0]}}"
        python -c "import pat3dem.main as p3m; p3m.driftcor_ctf_ptclpick('$f', '{cluster}')"
        f="$fnew"
    fi
done <"{PROJECT_FOLDER}/rawmovies/f.txt"

fstat="$( stat {PROJECT_FOLDER}/rawmovies/$f )"; sleep 30s
while [ "$fstat" != "$( stat {PROJECT_FOLDER}/rawmovies/$f )" ]
do
    fstat="$( stat {PROJECT_FOLDER}/rawmovies/$f )"; sleep 30s
done
IFS='/'; fsplit=($f); unset IFS
cd "{PROJECT_FOLDER}/motioncor2/${{fsplit[0]}}"
python -c "import pat3dem.main as p3m; p3m.driftcor_ctf_ptclpick('$f', '{cluster}')"
printf 'All preprocessing jobs have been submitted!\\n\\n'
"""
	context = {
	"PROJECT_FOLDER":os.environ['PROJECT_FOLDER'],
	 "cluster":cluster
	 }
	fscript = "{}_p3.sh".format(out)
	with open(fscript, 'w') as f:
		f.write(template.format(**context))
	import pat3dem.cluster as p3c
	getattr(p3c, cluster)(fscript, out, 168, 1, 1, 1, 1, 1, 0)	

def get_coord(coord_str):
	# return the coord range, defined by the coord_str containing num and space, e.g., '8 7 1 6' will return [7, 8, 1, 6]
	c_list = coord_str.split()
	c_len = len(c_list)
	coord_range = []
	for i in xrange(c_len/2):
		num1 = int(c_list[i*2])
		num2 = int(c_list[i*2+1])
		num = [num1, num2]
		if num1 > num2:
			num = [num2, num1]
		coord_range += num
	return coord_range

def set_value(d, coord_str, value):
	# set value in d, d = EMData(image), the range is defined by coord_str
	coord_range = get_coord(coord_str)
	c_len = len(coord_range)
	if c_len == 6:
		x1, x2, y1, y2, z1, z2 = coord_range
		for x in xrange(x1, x2+1):
			for y in xrange(y1, y2+1):
				for z in xrange(z1, z2+1):
					d.set_value_at(x, y, z, value)
	else:
		sys.exit('Not 3D coordinates?!')
	return d

def get_value(image, coord_str):
	# return a dictionary, {position1:value1, ..., position2:value2}, positions are from image, and defined by coord_str
	print '\nIn {},'.format(image)
	d = EMData(image)
	p_dict = {}
	coord_range = get_coord(coord_str)
	c_len = len(coord_range)
	if c_len == 6:
		x1, x2, y1, y2, z1, z2 = coord_range
		for x in xrange(x1, x2+1):
			for y in xrange(y1, y2+1):
				for z in xrange(z1, z2+1):
					value = d.get_value_at(x, y, z)
					print '({}, {}, {}): {}'.format(x, y, z, value)
					p_dict[(x, y, z)] = value
	else:
		sys.exit('Not 3D coordinates?')
	return p_dict

def plot_hist(num_list, out):
	# read a num list, plot a histogram and save to out
	plt.hist(num_list)
	plt.title("Histogram")
	plt.xlabel("Value")
	plt.ylabel("Frequency")
	plt.savefig(out)
	plt.close()
	