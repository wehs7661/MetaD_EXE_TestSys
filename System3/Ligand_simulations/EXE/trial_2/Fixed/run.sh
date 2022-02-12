#!/bin/sh
#SBATCH --job-name ligand_2
#SBATCH -p RM
#SBATCH -N 6
#SBATCH -t 48:00:00
#SBATCH --ntasks-per-node=28

source /home/wehs7661/src/plumed2/sourceme.sh
source /home/wehs7661/pkgs/gromacs/2020.2/bin/GMXRC
module load gcc/10.1.0
module load mpi/intel_mpi

# export OMP_NUM_THREADS=24

mpirun -np 168 gmx_mpi mdrun -s sys3_gst.tpr -x sys3_gst.xtc -c sys3_gst_output.gro -e sys3_gst.edr -dhdl sys3_gst_dhdl.xvg -g sys3_gst.log -cpi state.cpt
