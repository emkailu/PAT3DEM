#!/usr/bin/env python

import subprocess

def ada(cmd, title, walltime, cpu, ptile):
	# submit a job to ada
	header = "#BSUB -J {}\n#BSUB -L /bin/bash\n#BSUB -W {}:00\n#BSUB -n {}\n#BSUB -M 4000\n#BSUB -o jobstatus.%J\n#BSUB -R 'span[ptile={}]'\n#BSUB -P 082861617408\nsource ~/.bashrc\n\n".format(title, walltime, cpu, ptile)
	with open(title+'.job', 'w') as job:
		job.write(header)
		job.write('{} > {}.log'.format(cmd, title))
	with open('zz.sh', 'w') as zz:
		zz.write('bsub < {}.job'.format(title))
	subprocess.call(['sh', 'zz.sh'])	

