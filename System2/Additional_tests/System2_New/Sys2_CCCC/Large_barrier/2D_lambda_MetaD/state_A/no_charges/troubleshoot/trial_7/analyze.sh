plumed driver --mf_xtc sys2_cccc.xtc --plumed plumed_bond_length.dat
plot_2d -f bond_length.dat -x "Time (ps)" -y "Bond length" -t "Bond length between atoms 1 and 2" -n bond_length_12 -fx 0.002
plot_2d -f bond_length.dat -x "Time (ps)" -y "Bond length" -t "Bond length between atoms 2 and 3" -n bond_length_23 -c 2 -fx 0.002
plot_2d -f bond_length.dat -x "Time (ps)" -y "Bond length" -t "Bond length between atoms 3 and 4" -n bond_length_34 -c 3 -fx 0.002
combine_plots -f bond_length_12.png bond_length_23.png bond_length_34.png -b -d 3 1 -s 30 8 -n bond_length
plot_2d -f HILLS_2D -x "Time (ps)" -y "Gaussian height (kT)" -cy "kJ/mol to kT" -n hills
