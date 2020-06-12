#!/bin/sh

for (( i=0; i<9; i=i+1 ))
do
    mkdir state_${i}
    cp *gro *top state_${i}
    cd state_${i}
    cp ../sys2_vanilla.0.mdp sys2_vanilla.${i}.mdp
    sed -i -e "s/init-lambda-state        = 0/init-lambda-state        = ${i}/g" sys2_vanilla.${i}.mdp
    gmx grompp -f sys2_vanilla.${i}.mdp -c *gro -p *top -o sys2.${i}.tpr
    cd ../
done

mkdir Init
mv *gro *top *mdp Init

for (( i=0; i<9; i=i+1 ))
do
    cd state_${i}
    gmx mdrun -deffnm sys2.${i} -dhdl sys2.${i}.dhdl.xvg
    cd ../
done


