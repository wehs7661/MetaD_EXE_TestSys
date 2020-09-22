This folder contains additional tests of System 2, in which we increased the magnitude of the force constant of the dihedral potential relevant to the intramolecular hydrogen bond. We tried to make the free energy barrier in the torsional space larger such that expanded ensemble and 1D lambda MetaD would not be able to give a correct estimate of the free energy difference even if the system is able to sample all the intermediate states (since the system was not able to sample all the configuations in the torsional space). To design such a case, we have to make sure the following things happen after the topology is modified: 
- With a metadynamics in theta, it should be shown that at lambda=0 and lambda=1, there is a large free energy barrier in the torsional space that can trap the system.
- We should have two metastable states, say state 1 and state 2, in the torsional space. If the free energy barrier is large enough, the expanded ensemble starting from state 1 and 2 should give statistically different estiamte of free energy difference between lambda=0 and lambda=1.

Here we tested several different values of force constants and for each trial, here is what we've done:
- We first copied Prep folder and deleted the output files and irrelevant files
-  We changed the force constant of the dihedral potential relavant to atoms 4 (O), 2 (C), 1 (C), and 5 (C) from -2.4996348 to the desired value (Line 124 in system.top).
- We re-performed energy minimization, equilibration and the short MD simulation with the modified topology file (system.top). In Final_inputs folder, the .gro file is the output .gro file of the short MD, while the .top file is the modified .top file.
- With the input files (.top and .gro files) we performed 1D MetaD in theta while fixing the lambda value at 0 and 1, respectively. We examined if there is an energy barrier in the torsional space. Simulations with different force constants are stored in the folder `theta_MetaD`. We extracted configurations at state 1 and state 2 for later use.
- If there was an energy barrier in the torsional space, we then performed an expanded ensemble starting from state 1 and state 2 (using the configurations extracted from `theta_MetaD`) and examine if the obtained free energy differences (between lambda=0 and lambda=1) are statistically different. 
- If the free energy differences are statistically different, we performed a 2D lambda MetaD and show that all the theta values are sampled. Since we have already shown that 2D lambda MetaD is able to give correcto free energy difference in the case that the torsional barrier has not been elevated, we should get a good estiamte of free energy difference in this new case as long as the system is able to sample all the states. 





