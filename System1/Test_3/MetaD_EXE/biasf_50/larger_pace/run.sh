for i in {1..20}
  do 
      cd rep_$i
      gmx mdrun -s sys1.tpr -x sys1.xtc -c sys1_output.gro -e sys1.edr -dhdl sys1_dhdl.xvg -g sys1.log -plumed
      cd ../
  done
