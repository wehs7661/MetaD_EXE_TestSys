# Test 3: Comparison between expanded ensemble and well-tempered MetaD-EXE
###### tags: `MetaD-EXE-TestSys` `System2`
As mentioned, in Test 3, Simulation 1 is an expanded ensemble simulation with weights updated by the Wang-Landau algorithm (`wl-scale`=0.8 this time), while Simulation 2 is a well-tempered alchemical metadynamics. 
### 1. Simulation 1: Expanded ensemble simulation with updating weights
- Path in the repository: `MetaD_EXE_TestSys/System1/Test_3/EXE_updating`
- In contrast to Simulation 1 in Test 2, instead of using a `wl-scale` very close to 1, here we specify `wl-scale` as 0.8 to compare expanded ensemble simulation with well-tempered alchemical metadynamics. All the other parameters used in the GROMACS `.mdp` file are the same.
- Similarly, the simulation is conducted with exactly the same 9 alchemical states used previously at 298 K for 5 ns. (Check the `.mdp` file in the repository for more details.)
- Commands
    - `gmx grompp -f sys2_expanded.mdp -c sys2.gro -p sys2.top -o sys2.tpr`
    - `gmx mdrun -s sys2.tpr -x sys2.xtc -c sys2_output.gro -e sys2.edr -dhdl sys2_dhdl.xvg -g sys2.log`
- As a result, it took about 57 minutes to finish the simulation.

### 2. Simulation 2: well-tempered alchemical metadynamics
- Path in the repository: `MetaD_EXE_TestSys/System2/Test_3/MetaD_EXE`
- The PLUMED input file used in this simulation is shown as follows:
  ```
  lambda: EXTRACV NAME=lambda

  METAD ...
  ARG=lambda
  SIGMA=0.01     # small SIGMA ensure that the Gaussian approaximate a delta function
  HEIGHT=0.5     # In this case, the wegiths in EXE_fixed are fixed, meaning no biasing potentials added     
  PACE=10        # should be nstexpanded
  GRID_MIN=0     # index of alchemical states starts from 0
  GRID_MAX=8     # we have 6 states in total
  GRID_BIN=8
  TEMP=298
  BIASFACTOR=3.24  
  LABEL=metad    
  FILE=HILLS_LAMBDA
  ... METAD

  PRINT STRIDE=10 ARG=lambda,metad.bias FILE=COLVAR
  ```
- As shown above, the PLUMED input file is basically the same as the one used in Simulation 2 in Test 2 of Test system 2 except that we now specify the temperature (`TEMP`) as 298 K (which is the same as `ref_t` specified in the GROMACS `.mdp` file) and the bias factor (`BIASFACTOR`) as 3.24. This value is calculated the same as what we did in [Test 3: Examination of biasing potentials in well-tempered MetaD-EXE](/DCS_mbp5Tb-_OtYkfNM4zw) for the first test system. 
- Command
With the same `.tpr` file as the one used in Simulation 1, we can simply execute the following command to run the simulation: `gmx mdrun -s sys2.tpr -x sys2.xtc -c sys2_output.gro -e sys2.edr -dhdl sys2_dhdl.xvg -g sys2.log -plumed`
- As a result, it took about 51.6 minutes to finish the simulation.
### 3. Comparison of the results between the simulations
- Final histogram
The final counts of Simulation 1 are:
  ```
              MC-lambda information
   N  CoulL   VdwL    Count   G(in kT)  dG(in kT)
   1  0.000  0.000    13776    0.00000    7.67256
   2  0.200  0.000    11901    7.67256    6.20920
   3  0.500  0.000    11877   13.88177    3.02108
   4  1.000  0.000    13516   16.90285    1.90540
   5  1.000  0.200    12248   18.80824    1.74157
   6  1.000  0.400    14788   20.54981    0.68204 <<
   7  1.000  0.600    15091   21.23185   -3.54133
   8  1.000  0.800     6630   17.69051   -2.80432
   9  1.000  1.000     6415   14.88619    0.00000
  ```
  On the other hand, the final counts of Simulation 2 are:
  ```
              MC-lambda information
   N  CoulL   VdwL    Count   G(in kT)  dG(in kT)
   1  0.000  0.000   138686  -26.30809    6.64064 <<
   2  0.200  0.000    41906  -19.66745    5.61827
   3  0.500  0.000    15953  -14.04918    2.22292
   4  1.000  0.000    10115  -11.82625    1.64463
   5  1.000  0.200     7535  -10.18162    1.48436
   6  1.000  0.400     6022   -8.69726    0.25753
   7  1.000  0.600     5742   -8.43973   -3.07355
   8  1.000  0.800     9453  -11.51328   -2.14514
   9  1.000  1.000    14588  -13.65842    0.00000
  ```
  And here are the final histograms (left: Simulation 1; right: Simulation 2):
<center><img src=https://i.imgur.com/wtgLmyT.png width=345><img src=https://i.imgur.com/wkX6vx9.png width=345></center>
  As shown above, apparently, MetaD-EXE did not perform as well as standard expanded ensemble. This might be a matter of `BIASFACTOR`, but we have to look into the problem to see if there is anything wrong except for the bias factor. 

- Exploration of state as a function of time
As shown below, the state as a function of time reflects the histogram above. in Simulation 1, the weights were equilibrated at 2.875 ns. The system was able to sample all the states frequently, but the last two states were significantly less sampled. On the other hand, in Simulation 2, the system was also able to sample all the states, but not as frequently as in Simulation 1. The system was sampling the first two states most of the time. 
<center><img src=https://i.imgur.com/IxLK6Fd.png width=345><img src=https://i.imgur.com/sf8AHK1.png width=345></center>

- Free energy difference
The solvation free energy is estimated based on Simulation 1 as follows:
  ```
  ====== Results ======
  Statistical inefficiency of dHdl: 1.2775869369506836
  Statistical inefficiency of u_nk: 1.0

  TI: 17.346067712560778 +/- 0.4395560964511634 kT
  BAR: 16.342514315148513 +/- unknown kT
  MBAR: 16.386114373893324 +/- 0.4208061041630449 kT
  ```
  On the other hand, below is the result of solvation free energy estimation based on Simulation 2:
  ```
  ====== Results ======
  Statistical inefficiency of dHdl: 2.0998973846435547
  Statistical inefficiency of u_nk: 1.0068646669387817

  TI: 18.227115803511964 +/- 0.7200117379897133 kT
  BAR: 17.11753669247424 +/- unknown kT
  MBAR: 17.367490062820238 +/- 0.7462561924366314 kT
  ```
  Given the standard deviation of the values presented above, the results of the two simulations are statistically consistent with each other. However, the estimations based on Simulation 2 might be less accurate due to the lack of sampling.
- Comparison of free energy calculations across different tests
Here we compare the free energy difference (units: kT) calculated from different simulations across different tests (Note: T1S1 means Simulation 1 in Test 1):
(Table to be presented)
- Overlap matrix
If the sampling is sufficient, the overlap matrix should be at least tridiagonal. As shown below, both matrices meet this requirement and the overlap between states is significant.
<center><img src=https://i.imgur.com/RxKgtsM.png width=345><img src=https://i.imgur.com/JAx3F4g.png width=345></center>