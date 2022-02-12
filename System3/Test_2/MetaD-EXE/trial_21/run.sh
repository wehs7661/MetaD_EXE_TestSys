#!/bin/sh
#SBATCH --job-name trial_21
#SBATCH -p RM
#SBATCH -N 1
#SBATCH -t 48:00:00
#SBATCH --ntasks-per-node=128

source /jet/home/wehs7661/pkgs/gromacs/2020.4/bin/GMXRC
source /jet/home/wehs7661/src/plumed2/sourceme.sh
module load gcc/10.2.0
module load openmpi/3.1.6-gcc10.2.0

mpirun -np 128 gmx_mpi mdrun -s sys3.tpr -x sys3.xtc -c sys3_output.gro -e sys3.edr -dhdl sys3_dhdl.xvg -g sys3.log -cpi state.cpt -plumed -ntomp 1
