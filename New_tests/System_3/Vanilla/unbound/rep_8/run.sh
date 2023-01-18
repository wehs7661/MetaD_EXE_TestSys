#!/bin/sh
#SBATCH --job-name unbound_8
#SBATCH -p RM
#SBATCH -N 1
#SBATCH -t 12:00:00
#SBATCH --ntasks-per-node=128

source /jet/home/${USER}/src/PLUMED/plumed2.8.0/plumed2/sourceme.sh
source /jet/home/${USER}/pkgs/gromacs/2021.4/bin/GMXRC
module load gcc/10.2.0
module load openmpi/3.1.6-gcc10.2.0

mpirun -np 64 gmx_mpi mdrun -s sys3.tpr -x sys3_md.xtc -c sys3_output.gro -g md.log -e md.edr -cpi state.cpt
