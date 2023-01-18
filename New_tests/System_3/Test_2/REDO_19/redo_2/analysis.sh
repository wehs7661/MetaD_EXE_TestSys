#!/bin/sh
#SBATCH --job-name sys3_analysis
#SBATCH -p RM
#SBATCH -N 1
#SBATCH -t 12:00:00
#SBATCH --ntasks-per-node=128

source /jet/home/${USER}/src/PLUMED/plumed2.8.0/plumed2/sourceme.sh
source /jet/home/${USER}/pkgs/gromacs/2021.4/bin/GMXRC
module load gcc/10.2.0
module load openmpi/3.1.6-gcc10.2.0

python bootstrap_estimator.py -d ./ -n 20 50 100 200 500 1000 2000 -hh HILLS_2D -t 0.25 -a 0.75
