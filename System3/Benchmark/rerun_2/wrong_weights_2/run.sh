#!/bin/sh
#SBATCH --job-name rerun_2
#SBATCH -p RM
#SBATCH -N 4
#SBATCH -t 24:00:00
#SBATCH --ntasks-per-node=7

source /home/wehs7661/src/plumed2/sourceme.sh
source /home/wehs7661/pkgs/gromacs/2020.2/bin/GMXRC
module load gcc/10.1.0
module load mpi/intel_mpi

# export OMP_NUM_THREADS=24

mpirun -np 28 gmx_mpi mdrun -s sys3.tpr -x sys3.xtc -c sys3_output.gro -e sys3.edr -dhdl sys3_dhdl.xvg -g sys3.log -cpi state.cpt
