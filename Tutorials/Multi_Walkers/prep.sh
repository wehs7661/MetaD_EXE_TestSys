#!/bin/bash
set -e   # exit upon error
read -p "Please input the common part of the file names: " name
read -p "Plase input the number of walkers: " N
read -p "Do you want the algorithm implemented based on MPI or an external file? (mpi/file): " mode

ml gromacs/2018.3

gmx_mpi grompp -f production.mdp -po ${name}_mdout.mdp -c ${name}.gro -p ${name}.top -o ${name}.tpr -n ${name}.ndx -maxwarn 4

if [ ${mode} == "file" ]
then
    mkdir HILLS
    for (( i=0; i<$N; i=i+1 ))
    do
        cp ${name}.tpr ${name}${i}.tpr
        cp plumed_file.dat plumed.${i}.dat
        sed -i -e "s/WALKERS_N=0/WALKERS_N=${N}/g" plumed.${i}.dat
        sed -i -e "s/WALKERS_ID=0/WALKERS_ID=${i}/g" plumed.${i}.dat
    done
elif [ ${mode} == "mpi" ]
then
    for (( i=0; i<$N; i=i+1 ))
    do 
        cp ${name}.tpr ${name}${i}.tpr
    done
    cp plumed_mpi.dat plumed.dat
else
    echo "Wrong input! The implementation must be either MPI-based or file-based."
fi
rm ${name}.tpr

