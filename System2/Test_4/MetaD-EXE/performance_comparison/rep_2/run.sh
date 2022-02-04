#!/bin/sh
#SBATCH --job-name 2D_rep1
#SBATCH -p RM
#SBATCH -N 1
#SBATCH -t 24:00:00
#SBATCH --ntasks-per-node=64

source /jet/home/wehs7661/pkgs/gromacs/2020.4/bin/GMXRC
source /jet/home/wehs7661/src/plumed2/sourceme.sh
module load gcc/10.2.0
module load openmpi/3.1.6-gcc10.2.0

mpirun -np 64 gmx_mpi mdrun -s sys2.tpr -x sys2.xtc -c sys2_output.gro -e sys2.edr -dhdl sys2_dhdl.xvg -g sys2.log -cpi state.cpt -plumed plumed.dat
