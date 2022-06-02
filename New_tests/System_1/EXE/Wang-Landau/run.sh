#!/bin/sh
#SBATCH --job-name sys1_EXE
#SBATCH -p RM
#SBATCH -N 1
#SBATCH -t 24:00:00
#SBATCH --ntasks-per-node=128

source /jet/home/${USER}/src/PLUMED/plumed2.8.0/plumed2/sourceme.sh
source /jet/home/${USER}/pkgs/gromacs/2021.4/bin/GMXRC
module load gcc/10.2.0
module load openmpi/3.1.6-gcc10.2.0

mpirun -np 128 gmx_mpi mdrun -s sys1.tpr -x sys1_md.xtc -c sys1_14_md.gro -g md.log -e md.edr -cpi state.cpt
