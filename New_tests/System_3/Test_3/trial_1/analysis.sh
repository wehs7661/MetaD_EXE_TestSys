#!/bin/sh
#SBATCH --job-name sys3_test3
#SBATCH -p RM
#SBATCH -N 1
#SBATCH -t 48:00:00
#SBATCH --ntasks-per-node=128

source /jet/home/${USER}/src/PLUMED/plumed2.8.0/plumed2/sourceme.sh
source /jet/home/${USER}/pkgs/gromacs/2021.4/bin/GMXRC
module load gcc/10.2.0
module load openmpi/3.1.6-gcc10.2.0

python calculate_free_energy.py -d ./ -n 20 50 200 500 1000 2000 -hh HILLS_2D -t 0 -a 0.2
