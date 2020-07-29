cd rep_1
gmx mdrun -s sys2.tpr -x sys2.xtc -c sys2_output.gro -e sys2.edr -dhdl sys2_dhdl.xvg -g sys2.log -plumed
cd ../rep_2
gmx mdrun -s sys2.tpr -x sys2.xtc -c sys2_output.gro -e sys2.edr -dhdl sys2_dhdl.xvg -g sys2.log -plumed
cd ../rep_3
gmx mdrun -s sys2.tpr -x sys2.xtc -c sys2_output.gro -e sys2.edr -dhdl sys2_dhdl.xvg -g sys2.log -plumed
cd ../rep_4
gmx mdrun -s sys2.tpr -x sys2.xtc -c sys2_output.gro -e sys2.edr -dhdl sys2_dhdl.xvg -g sys2.log -plumed
cd ../rep_5
gmx mdrun -s sys2.tpr -x sys2.xtc -c sys2_output.gro -e sys2.edr -dhdl sys2_dhdl.xvg -g sys2.log -plumed
cd ../
