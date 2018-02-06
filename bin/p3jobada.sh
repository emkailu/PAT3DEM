echo '''#BSUB -J JobName
#BSUB -o JobName.%J
#BSUB -W 168:00
#BSUB -n 5
#BSUB -R "rusage[mem=10000]"
#BSUB -M 10000
#BSUB -R "span[ptile=3]"
#BSUB -R "select[gpu]"
#BSUB -P 082861611545
#BSUB -L /bin/bash

#source ~/.bashrc
module purge;module load OpenMPI/1.8.7-GCC-4.9.3;module load RELION/2.0-beta

mpirun -n 5 `which relion_refine_mpi` --o Refine3D/K10-7 --continue Refine3D/run1_it010_optimiser_K10-7.star --oversampling 1 --auto_local_healpix_order 4 --j 4 --gpu &>JobName.log
'''
