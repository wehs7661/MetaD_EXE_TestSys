# Test 2: Comparison between expanded ensemble and standard alchemical metadynamics

###### tags: `MetaD-EXE-TestSys` `TestSystem2
As mentioned, in Test 2, Simulation 1 is an expanded ensemble simulation with weights updated by the Wang-Landau algorithm (`wl_scale`= 0.999999), while Simulation 2 is a standard alchemical metadynamics. 

### 1. Simulation 1: Expanded ensemble simulation with updating weights
- Path in the repository: `MetaD_EXE_TestSys/System2/Test_2/EXE_updating`
- First copy the input `.gro` and `.top` files: `cp ../../Prep/Final_inputs/* .`, then copy the `.mdp` file from Test 1: `cp ../../Test_1/Vanilla/Init/sys2_vanilla.0.mdp .` and make sure the options related to expande ensemble are set up as below:
  ```=1
  ; Seed for Monte Carlo in lambda space
  lmc-seed                 = 1000
  lmc-gibbsdelta           = -1
  lmc-forced-nstart        = 0
  symmetrized-transition-matrix = yes
  nst-transition-matrix    = 100000
  wl-scale                 = 0.999999
  wl-ratio                 = 0.8
  init-wl-delta            = 0.5

  ; expanded ensemble variables
  nstexpanded              = 10
  lmc-stats                = wang-landau
  lmc-move                 = metropolized-gibbs
  lmc-weights-equil        = wl-delta
  weight-equil-wl-delta    = 0.0001

  ; lambda-states          = 1      2      3      4      5      6      7      8      9
  coul-lambdas             = 0.00   0.20   0.50   1.00   1.00   1.00   1.00   1.00   1.00
  vdw-lambdas              = 0.00   0.00   0.00   0.00   0.20   0.40   0.60   0.80   1.00
  ```
- Commands
    - `gmx grompp -f sys2.mdp -c sys2.gro -p sys2.top -o sys2.tpr`
    - `gmx mdrun -s sys2.tpr -x sys2.xtc -c sys2_output.gro -e sys2.edr -dhdl sys2_dhdl.xvg -g sys2.log`
    
### 2. Standard alchemical metadynamics
- Path in the repository: `/MetaD_EXE_TestSys/System2/Test_2/MetaD_EXE`
- Here we use the same `.tpr` file as Simulation 1 (hence the same GROMACS parameters). Similarly, we the same PLUMED input file as Simulation 2 in Test 2 except that the `HEIGHT` is specified as 0.5 instead of 0. 
- Commands
    - `gmx grompp -f sys2.mdp -c sys2.gro -p sys2.top -o sys2.tpr`
    - `gmx mdrun -s sys2.tpr -x sys2.xtc -c sys2_output.gro -e sys2.edr -dhdl sys2_dhdl.xvg -g sys2.log -plumed`

### 3. Comparison of the results between the simulations
- Data analysis of Simulation 1
  - Final histogram
![](https://i.imgur.com/LFQzI6A.png)
  - Exploration of state as a function of time
  ![](https://i.imgur.com/mXJe6wK.png)
  - Solvation free energy
  ```
  ====== Results ======
  Statistical inefficiency of dHdl: 1.0
  Statistical inefficiency of u_nk: 1.0

  TI: 11.605293494125881 +/- 1.028956867629661 kT
  BAR: 15.185090765179924 +/- unknown kT
  MBAR: 16.377046914318374 +/- 0.3286438123153898 kT
  ```
  - Overlap matrix
  ![](https://i.imgur.com/xll06SL.png)
  
- Data analysis of Simulation 2 </br>
In Simulation 2, an underflow happened at 0.162 ns as follows:
  ```
  Fatal error:
  Something wrong in choosing new lambda state with a Gibbs move -- probably
  underflow in weight determination.
  Denominator is:   0 1.0000000000e+00
    i                dE        numerator          weights
    0 -4.5607214355e+02 0.0000000000e+00-2.3800000000e+02
    1 -4.4794921875e+02 0.0000000000e+00-2.3050000000e+02
    2 -4.4151489258e+02 0.0000000000e+00-2.2500000000e+02
    3 -4.3795764160e+02 0.0000000000e+00-2.2300000000e+02
    4 -6.2703781128e+01 5.8626487139e-28-2.2050000000e+02
    5 -3.5630508423e+01 3.3563466130e-16-2.1850000000e+02
    6  0.0000000000e+00 1.0000000000e+00-1.8650000000e+02
    7 -3.5623397827e+01 3.3802972637e-16-2.2000000000e+02
    8 -3.9293258667e+01 8.6130024118e-18-2.2050000000e+02
  ```
  This is an issue that we are currently looking into.`