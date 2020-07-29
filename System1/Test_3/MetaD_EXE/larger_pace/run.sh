cd rep_1
gmx mdrun -s sys1.tpr -x sys1.xtc -c sys1_output.gro -e sys1.edr -dhdl sys1_dhdl.xvg -g sys1.log -plumed
cd ../rep_2
gmx mdrun -s sys1.tpr -x sys1.xtc -c sys1_output.gro -e sys1.edr -dhdl sys1_dhdl.xvg -g sys1.log -plumed
cd ../rep_3
gmx mdrun -s sys1.tpr -x sys1.xtc -c sys1_output.gro -e sys1.edr -dhdl sys1_dhdl.xvg -g sys1.log -plumed
cd ../rep_4
gmx mdrun -s sys1.tpr -x sys1.xtc -c sys1_output.gro -e sys1.edr -dhdl sys1_dhdl.xvg -g sys1.log -plumed
cd ../rep_5
gmx mdrun -s sys1.tpr -x sys1.xtc -c sys1_output.gro -e sys1.edr -dhdl sys1_dhdl.xvg -g sys1.log -plumed
cd ../
