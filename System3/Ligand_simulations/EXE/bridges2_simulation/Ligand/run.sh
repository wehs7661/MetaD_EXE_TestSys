#!/bin/sh
#SBATCH --job-name ligand
#SBATCH -p RM
#SBATCH -N 1
#SBATCH -t 36:00:00
#SBATCH --ntasks-per-node=128

source /jet/home/wehs7661/pkgs/gromacs/2020.4/bin/GMXRC
source /jet/home/wehs7661/src/plumed2/sourceme.sh
module load gcc/10.2.0
module load openmpi/3.1.6-gcc10.2.0

mpirun -np 128 gmx_mpi mdrun -s sys3_gst.tpr -x sys3_gst.xtc -c sys3_gst_output.gro -e sys3_gst.edr -dhdl sys3_gst_dhdl.xvg -g sys3_gst.log -cpi state.cpt
