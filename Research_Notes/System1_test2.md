# Test 2: Examination of biasing potentials in standard MetaD-EXE
###### tags: `MetaD-EXE-TestSys` `TestSystem1`
As mentioned above, in the second test, we want to really bias the alchemical variable with the standard metadynamics, in which the height of the Gaussian biasing potential remains constant throughout the simulation. To compare the results of this simulation, we specify `init-wl-delta` used in the expanded ensemble (Simulation 1) as the same value of `HEIGHT` used in alchemical metadynamics (Simulation 2) and set `wl-scale = 1` in Simulation 1 to make the Wang-Landau incrementor a constant. With these parameters, the results obtained from the two simulations, including the final histogram, the state as a function of time, and the free energy difference, should be similar. 

### 1. Simulation 1: expanded ensemble simulation with updating weights (`wl-scale` $\sim$ 1)
- Path in the repository: `MetaD_EXE_TestSys/System1/Test_2/EXE_updating`
- In contrast to Simulation 1 in Test 1, all the options related to Wang-Landau algorithm should be turned on, including `lmc-stats = wang-landau` instead of `no`, `wl-scale`, `wl-ratio`, and `weight-equil-wl-delta`.
- Note that in GROMACS, `wl-scale` can be not exactly set as 1, so use set it as 0.999999 instead. This makes the Wang-Landau approximately remain the same even after 10000 updates ($0.999999^{10000} \sim 0.99005$). Note that since the Wang-Landau incrementor barely decreases, it will "never" reach the criteria of the weight equilibration, which is that $\Delta w < 0.01$ specified in the GROMACS `.mdp` file.
- Similarly, the simulation is conducted with exactly the same 6 alchemical states used previously at 298 K for 5 ns. (Check the `.mdp` file in the repository for more details.)
- Commands
    - `gmx grompp -f sys1_expanded.mdp -c sys1.gro -p sys1.top -o sys1.tpr -maxwarn 1`
    - `gmx mdrun -s sys1.tpr -x sys1.xtc -c sys1.gro -e sys1.edr -dhdl sys1_dhdl.xvg -g sys1.log`
- As a result, it took about 16.3 minutes to finish the simulation.
    
### 2. Simulation 2: Standard alchemical metadynamics (constant Gaussian height)
- Path in the repository: `MetaD_EXE_TestSys/System1/Test_2/MetaD_EXE`
- The PLUMED input file used in this simulation is shown as follows:
  ```
  lambda: EXTRACV NAME=lambda

  METAD ...
  ARG=lambda
  SIGMA=0.01     # small SIGMA ensure that the Gaussian approximate a delta function
  HEIGHT=0.5     # should be equal to init-wl-delta in standard alchemical metadynamics
  PACE=10        # should be nstexpanded
  GRID_MIN=0     # index of alchemical states starts from 0
  GRID_MAX=5     # we have 6 states in total
  GRID_BIN=5     # we need 5 bins between 6 points
  LABEL=metad    # it's not clear how GRID parameters will have influences here
  FILE=HILLS_LAMBDA
  ... METAD

  PRINT STRIDE=10 ARG=lambda,metad.bias FILE=COLVAR
  ```
  The only difference between the PLUMED input file used here and the one used previously in Simulation 2 in Test 1 is that now `HEIGHT` is non-zero and equal to `init-wl-delta` specified in the GROMACS `.mdp` file.
- Command
With exactly the same `.tpr` file as Simulation 1 in Test 2, execute `gmx mdrun -s sys1.tpr -x sys1.xtc -c sys1_output.gro -e sys1.edr -dhdl sys1_dhdl.xvg -g sys1.log -plumed`.
- As a reulst, it took about 18.2 minutes to finish the simulation if `GRID_*` parameters are used.

### 3. Comparison of the results between the simulations
- The final histogram 
The final histogram of Simulation 1 is:
  ```
             MC-lambda information
  Wang-Landau incrementor is:     0.49894
  N   VdwL    Count   G(in kT)  dG(in kT)
  1  0.000        0    0.00000   -0.99796
  2  0.200        0   -0.99796   -1.99642
  3  0.400        3   -2.99438  -14.47342
  4  0.600       27  -17.46780   -4.49485
  5  0.800       32  -21.96265   -2.49550
  6  1.000       36  -24.45815    0.00000 <<
  ```
  As shown above, the first two states do not have any counts and the number of counts for all the states are quite low. This is just a result of the very high frequency of updating the Wang-Landau incrementor. As shown below, the time required to sample all the states is very short (only dozens of samples), making the histogram flat within a very short time as well. (1 ps corresponds to 50 counts since `nstexpanded = 10` and `dt = 0.002`.) Once the histogram is considered flat, the Wang-Landau incrementor is scaled by 0.999999 and the counts are reset to 0. Therefore, in this case, there is actually no points to compare the final histogram of the two simulations. <center><img src=https://i.imgur.com/MYrJcom.png width=500></center>
  However, we can still check the final counts of the states of Simulation 2:
  ```
             MC-lambda information
  N   VdwL    Count   G(in kT)  dG(in kT)
  1  0.000    41665 -10416.00000   -1.00000
  2  0.200    41667 -10417.00000    0.00000 <<
  3  0.400    41667 -10417.00000    0.50000
  4  0.600    41666 -10416.50000   -2.50000
  5  0.800    41666 -10419.00000   -1.50000
  6  1.000    41669 -10420.50000    0.00000
  ```
  As shown above, the weights estimated by alchemical metadynamics ensure a pretty flat histogram. In the current implementation, the weight of the first state was not shifted to 0 though, which is the problem we have to solve shortly.
- Exploration of state as a function of time
As shown below, the figure on the left is the result from Simulation 1, while the one on the right is the result from Simulation 2 (based on the `.log` file). All the states are well sampled in both simulations.
<center><img src=https://i.imgur.com/PyqenR1.png width=330><img src=https://i.imgur.com/QiJYqHN.png width=330></center> 

- Free energy difference 
The following is the result of free energy difference obtained from Simulation 1:
  ```
  ====== Results ======
  Statistical inefficiency of dHdl: 1.0
  Statistical inefficiency of u_nk: 1.0

  TI: -5.850162263194646 +/- 0.34724561859436376 kT
  BAR: -3.7597286154906557 +/- unknown kT
  MBAR: -2.4840745041533205 +/- 0.11515090177248272 kT
  ```
  On the other hand, the following is the result obtained from Simulation 2. 
  **Question**: The big difference in the free energy difference between different methods in Simulation 1.
  ```
  ====== Results ======
  Statistical inefficiency of dHdl: 1.0
  Statistical inefficiency of u_nk: 1.0

  TI: -5.027747585564408 +/- 0.2994803758956154 kT
  BAR: -3.715886270966177 +/- unknown kT
  MBAR: -3.012397511069156 +/- 0.12457272629404113 kT
  ```

- Overlap matrix
If the sampling is sufficient, the overlap matrix should be at least tridiagonal. As shown below, both matrices meet this requirement and the overlap between states is significant. 
<center><img src=https://i.imgur.com/NCFypph.png width=330><img src=https://i.imgur.com/uCC98nd.png width=330></center> 