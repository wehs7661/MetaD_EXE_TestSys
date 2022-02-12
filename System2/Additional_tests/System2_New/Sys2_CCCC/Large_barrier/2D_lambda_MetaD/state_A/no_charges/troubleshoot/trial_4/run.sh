gmx mdrun -s sys2_cccc.tpr -x sys2_cccc.xtc -c sys2_cccc_output.gro -e sys2_cccc.edr -dhdl sys2_cccc_dhdl.xvg -g sys2_cccc.log -plumed -cpi state.cpt

echo 10 11 | gmx energy -s *tpr -f *edr -o energy.xvg
echo 2 0 | gmx trjconv -s sys2_cccc.tpr -f sys2_cccc.xtc -o sys2_cccc_nojump.xtc -center -pbc nojump
echo 2 2 | gmx trjconv -s *tpr -f *nojump* -o sys2_cccc_center.pdb -center -pbc mol -ur compact

plumed driver --mf_xtc *xtc --plumed plumed_dihedral.dat
plumed driver --mf_xtc *xtc --plumed plumed_bond_length.dat
plumed driver --plumed plumed_sum_bias.dat --noatoms

plumed sum_hills --hills HILLS_2D --bin 200,7 --negbias --mintozero --outfile negbias_2d.dat
plumed sum_hills --hills HILLS_2D --bin 200,7 --idw theta --kt 2.478956208925815 --negbias --mintozero --outfile negbias_dihedral.dat

plot_2d -f energy.xvg -x "Time (ps)" -y "Potential energy (kJ/mol)" -n potential_whole
plot_2d -f energy.xvg -x "Time (ps)" -y "Potential energy (kJ/mol)" -tr 99.9 -n potential_last0.1
plot_2d -f energy.xvg -x "Time (ps)" -y "Potential energy (kJ/mol)" -c 2 -n kinetic_whole
plot_2d -f energy.xvg -x "Time (ps)" -y "Potential energy (kJ/mol)" -c 2 -tr 99.9 -n kinetic_last0.1
plot_2d -f bond_length.dat -x "Time (ps)" -y "Bond length 1-2 (nm)" -n bond_length12
plot_2d -f bond_length.dat -x "Time (ps)" -y "Bond length 2-3 (nm)" -n bond_length23 -c 2
plot_2d -f bond_length.dat -x "Time (ps)" -y "Bond length 3-4 (nm)" -n bond_length34 -c 3
plot_2d -f HILLS_2D -x "Time (ps)" -y "Gaussian height (kT)" -cy "kJ/mol to kT" -n hills

combine_plots -f potential_whole.png kinetic_whole.png -s 20 8 -b -n energy_whole
combine_plots -f potential_last0.1.png kinetic_last0.1.png -s 20 8 -b -n energy_last0.1
combine_plots -f bond_length12.png bond_length23.png bond_length34.png -d 3 1 -s 30 8 -b -n bond_length
