gmx grompp -f sys2_expanded.mdp -c sys2_cccc.gro -p sys2_cccc.top -o sys2_cccc.tpr
gmx mdrun -s sys2_cccc.tpr -x sys2_cccc.xtc -c sys2_cccc_output.gro -e sys2_cccc.edr -dhdl sys2_cccc_dhdl.xvg -g sys2_cccc.log -plumed
