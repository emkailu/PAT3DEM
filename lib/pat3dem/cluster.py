#!/usr/bin/env python

import subprocess
import paramiko

def ada(cmd, title, walltime, cpu, ptile):
	# submit a job to ada
	# title is usually the root name for output
	header = "#BSUB -J {}\n#BSUB -L /bin/bash\n#BSUB -W {}:00\n#BSUB -n {}\n#BSUB -R 'rusage[mem=10000]'\n#BSUB -M 10000\n#BSUB -o jobstatus.%J\n#BSUB -R 'span[ptile={}]'\n#BSUB -P 082861613633\nsource ~/.bashrc\n\n".format(title, walltime, cpu, ptile)
	with open(title+'.job', 'w') as job:
		job.write(header)
		job.write('{} > {}.log\n'.format(cmd, title))
	with open('zz.sh', 'w') as zz:
		zz.write('bsub < {}.job\n'.format(title))
	subprocess.call(['sh', 'zz.sh'])
	
def ada_quota():
	# return the remaining disk (in GB) and nfile
	disk = 0
	nfile = 0
	with open('quota.log', 'w') as log:
		subprocess.call(['showquota'], stdout=log, stderr=subprocess.STDOUT)
	with open('quota.log') as log:
		lines = log.readlines()
		for i in lines:
			if i[:8] == '/scratch':break
	i = i.split()
	nfile = int(i[-1]) - int(i[-2])
	d_total, d_used = i[-3], i[-4]
	d_total = float(d_total.replace('T', '')) * 1000
	if 'T' in d_used:
		d_used = float(d_used.replace('T', '')) * 1000
	elif 'G' in d_used:
		d_used = float(d_used.replace('G', ''))
	elif 'M' in d_used:
		d_used = float(d_used.replace('M', '')) / 1000.0
	d = d_total - d_used
	return d, nfile

def chiu_download(i, j, com_par):
	# download a file specified by i from chiu to a local file specified by j
	# both i and j include path
	s=paramiko.SSHClient()
	s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	s.connect("chiu.tamu.edu",22,username='kailu',password=com_par['p'])
	sftp = s.open_sftp()
	sftp.get(i, j)
	
