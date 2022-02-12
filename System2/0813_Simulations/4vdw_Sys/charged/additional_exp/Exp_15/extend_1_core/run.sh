#!/bin/sh
#SBATCH --job-name extend_1
#SBATCH -p RM
#SBATCH -N 1
#SBATCH -t 48:00:00
#SBATCH --ntasks-per-node=1

source /jet/home/wehs7661/pkgs_1/gromacs/2020.4/bin/GMXRC
source /jet/home/wehs7661/src_1/plumed2/sourceme.sh
module load gcc/10.2.0

gmx mdrun -s sys2_cccc.tpr -o sys2_cccc.trr -c sys2_cccc_output.gro -e sys2_cccc.edr -dhdl sys2_cccc_dhdl.xvg -g sys2_cccc.log -plumed -cpi state.cpt -ntomp 1 -nt 1
