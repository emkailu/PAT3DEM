#!/usr/bin/env python

import os
import subprocess
import paramiko

def sherlock(cmd, out, walltime, nnodes, ntasks, ntasks_per_node, cpu_per_task, mem_per_node, gpu_per_node):
	# submit a job to terra, the 'cmd' can be a command, or a .sh file containing commands
	# specify gpu_per_node as 0, if you don't want to use gpu
	# ntasks_per_node is not used
	out = out + '_p3'
	if gpu_per_node == 0:
		gpu = ''
	else:
		gpu = "#SBATCH --gres=gpu:{}\n".format(gpu_per_node)
	header = "#!/bin/bash\n#SBATCH --job-name=test\n#SBATCH --time={}:00:00\n#SBATCH --nodes={}\n#SBATCH --ntasks={}\n#SBATCH --cpus-per-task={}\n#SBATCH --mem={}G\n#SBATCH --output={}.%j\n#SBATCH -p brunger\n{}source ~/.bashrc\n\n".format(walltime, nnodes, ntasks, cpu_per_task, mem_per_node, out, gpu)
	with open(out+'.job', 'w') as job:
		job.write(header)
		if os.path.isfile(cmd):
			if cmd[-3:] == '.sh':
				job.write('srun sh {} > {}.log\n'.format(cmd, out))
		else:
			job.write('srun {} > {}.log\n'.format(cmd, out))
	with open('.p3.sh', 'w') as zz:
		zz.write('sbatch {}.job\n'.format(out))
	subprocess.call(['sh', '.p3.sh'])

def terra(cmd, out, walltime, nnodes, ntasks, ntasks_per_node, cpu_per_task, mem_per_node, gpu_per_node):
	# submit a job to terra, the 'cmd' can be a command, or a .sh file containing commands
	# specify gpu_per_node as 0, if you don't want to use gpu
	# nnodes, cpu_per_task are not used
	out = out + '_p3'
	if gpu_per_node == 0:
		gpu = ''
	else:
		gpu = "#SBATCH --gres=gpu:{}\n#SBATCH -p gpu\n".format(gpu_per_node)
	header = "#!/bin/bash\n#SBATCH --job-name=test\n#SBATCH --time={}:00:00\n#SBATCH --ntasks={}\n#SBATCH --ntasks-per-node={}\n#SBATCH --mem={}G\n#SBATCH --output={}.%j\n#SBATCH -A 122792648842\n{}source ~/.bashrc\n\n".format(walltime, ntasks, ntasks_per_node, mem_per_node, out, gpu)
	with open(out+'.job', 'w') as job:
		job.write(header)
		if os.path.isfile(cmd):
			if cmd[-3:] == '.sh':
				job.write('sh {} > {}.log\n'.format(cmd, out))
		else:
			job.write('{} > {}.log\n'.format(cmd, out))
	with open('.p3.sh', 'w') as zz:
		zz.write('sbatch {}.job\n'.format(out))
	subprocess.call(['sh', '.p3.sh'])
	
def ada(cmd, out, walltime, cpu, ptile):
	# submit a job to ada
	out = out + '_p3'
	header = "#BSUB -J {}\n#BSUB -L /bin/bash\n#BSUB -W {}:00\n#BSUB -n {}\n#BSUB -R 'rusage[mem=10000]'\n#BSUB -M 10000\n#BSUB -o jobstatus.%J\n#BSUB -R 'span[ptile={}]'\n#BSUB -P 082861617408\nsource ~/.bashrc\n\n".format(out, walltime, cpu, ptile)
	with open(out+'.job', 'w') as job:
		job.write(header)
		job.write('{} > {}.log\n'.format(cmd, out))
	with open('.p3.sh', 'w') as zz:
		zz.write('bsub < {}.job\n'.format(out))
	subprocess.call(['sh', '.p3.sh'])
	
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
	
def server_download(i, j, c_p):
	# download a file specified by i from a server to a local file specified by j
	# both i and j include path
	s=paramiko.SSHClient()
	s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	s.connect(c_p['s'],22,username=c_p['u'],password=c_p['p'])
	sftp = s.open_sftp()
	i = '{}/{}'.format(c_p['dp'], i)
	sftp.get(i, j)
	

	
