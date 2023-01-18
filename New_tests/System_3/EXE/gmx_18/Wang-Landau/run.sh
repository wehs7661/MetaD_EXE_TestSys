#!/bin/sh
#SBATCH --job-name sys3_EXE
#SBATCH -p RM
#SBATCH -N 1
#SBATCH -t 48:00:00
#SBATCH --ntasks-per-node=128

module load gromacs/2018
module load gcc/10.2.0
module load openmpi/3.1.6-gcc10.2.0

mpirun -np 128 gmx_mpi mdrun -s sys3.tpr -x sys3_EXE.xtc -c sys3_EXE.gro -g EXE.log -e EXE.edr -cpi state.cpt
