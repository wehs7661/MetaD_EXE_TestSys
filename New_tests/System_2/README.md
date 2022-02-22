Here in different trials we were testing out different charges and force constant to make the difference in the free energy differences obtained from 1D alchemical metadynamics starting from different metastable states (1) large enough to show statistical inconcistency between the results and (2) small enough such that the less stable state can at least get moderately sampled. 

- trial_1: total charges = +/- 0.3, force constant = 60
    - Length: 100 ns   
    - Starting from state A: 6.586 +/- 0.046 kT 
    - Starting from state B: 4.097 +/- 0.046 kT
    - Note that the box sizes in the case are not exactly the same, which would probably cause a small difference … but we decided to lower the charges since a fix in the box size probably won’t decrease the difference between state A and B values too much ...

- trial_2: total charges = +/- 0.3, force constant = 30
    - Length: 50 ns
    - Starting from state A: not calculated but should be around 5.5 kt or so
    - Starting from state B: not finished because we think another trial (not presented here, charges=+/-0.2, force constant=60) is better 


