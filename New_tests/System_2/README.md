Here in different trials we were testing out different charges and force constant to make the difference in the free energy differences obtained from 1D alchemical metadynamics starting from different metastable states (1) large enough to show statistical inconcistency between the results and (2) small enough such that the less stable state can at least get moderately sampled. 

All simulations here were accidentally using output files from an NPT MD simulations for alchemical metadynamcis (including 1D and 2D) in the NVT ensemble, so we archived the simulations using the wrong input structures here. In alchemical_MetaD now, we are using the set of parameters in trial_3 but with correct inputs.

- trial_1: total charges = +/- 0.3, force constant = 60
    - Length: 100 ns   
    - Starting from state A: 6.586 +/- 0.046 kT 
    - Starting from state B: 4.097 +/- 0.046 kT
    - Note that the box sizes in the case are not exactly the same, which would probably cause a small difference … but we decided to lower the charges since a fix in the box size probably won’t decrease the difference between state A and B values too much ...

- trial_2: total charges = +/- 0.3, force constant = 30
    - Length: 50 ns
    - Starting from state A: not calculated but should be around 5.5 kt or so
    - Starting from state B: not finished because we think another trial (not presented here, charges=+/-0.2, force constant=60) is better 

- trial_3: total charges = +/- 0.2, force constant = 60
    - Adopted case.
    - Length: 100 ns, later extended to 200 ns.
    - Starting from state A (100 ns): -0.735 +/- 0.065 kT
    - Starting from state B (100 ns): -1.907 +/- 0.070 kT

