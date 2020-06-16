# Test 3: Examination of biasing potentials in well-tempered MetaD-EXE

###### tags: `MetaD-EXE-TestSys`
### 1. Simulation 1: expanded ensemble simulation with updating weights (`wl-scale`=0.8)
- Path in the repository: `MetaD_EXE_TestSys/System1/Test_3/EXE_updating`
- In contrast to Simulation 1 in Test 2, instead of using a `wl-scale` very close to 1, here we specify `wl-scale` as 0.8 to compare expanded ensemble simulation with well-tempered alchemical metadynamics. All the other parameters used in the GROMACS `.mdp` file are the same. 
- Similarly, the simulation is conducted with exactly the same 6 alchemical states used previously at 298 K for 5 ns. (Check the `.mdp` file in the repository for more details.)
- Commands
    - `gmx grompp -f sys1_expanded.mdp -c sys1.gro -p sys1.top -o sys1.tpr -maxwarn 1`
    - `gmx mdrun -s sys1.tpr -x sys1.xtc -c sys1_output.gro -e sys1.edr -dhdl sys1_dhdl.xvg -g sys1.log`
- As a result, it took about 17 minutes to finish the simulation.

### 2. Simulation 2: well-tempered alchemical metadynamics
- Path in the repository: `MetaD_EXE_TestSys/System1/Test_3/MetaD_EXE`
- The PLUMED input file used in this simulation is shown as follows:
  ```
  lambda: EXTRACV NAME=lambda

  METAD ...
  ARG=lambda
  SIGMA=0.01     # small SIGMA ensure that the Gaussian approaximate a delta function
  HEIGHT=0.5     # should be equal to init-wl-delta
  PACE=10        # should be nstexpanded
  GRID_MIN=0     # index of alchemical states starts from 0
  GRID_MAX=5     # we have 6 states in total
  GRID_BIN=5     # 5 bins between 6 states
  TEMP=298       # same as ref_t
  BIASFACTOR=3.24    # equivalent as wl-scale assuming periodic wl-weights updating
  LABEL=metad    # it's not clear how GRID parameters will have influences here
  FILE=HILLS_LAMBDA
  ... METAD

  PRINT STRIDE=10 ARG=lambda,metad.bias FILE=COLVAR
  ```
- As shown above, the PLUMED input file is basically the same as the one used in Test 2 of Test system 1 except that we now specify the temperature (`TEMP`) as 298 K (which is the same as `ref_t` specified in the GROMACS `.mdp` file) and the bias factor (`BIASFACTOR`) as 3.24.
- As mentioned in the section addressing the equivalence between EXE and MetaD-EXE in the note of [implemntation details](/1UNHd7vxTRiVAbPA7HW8vg), `wl-scale` in GROMACS is not exactly equivalent to `BIASFACTOR` in PLUMED since the former does not update the bias periodically as the latter does. To make the results of the simulations as comparable to each other as possible, we assume that `wl-scale` updates the Wang-Landau incrementor approximately as frequently as `BIASFACTOR` updates the height of the biasing potential (which is actually unlikely to happen). Here, we start with the following equation derived in the note linked above:
$$s_{eff} = \exp (-\frac{V(\vec{s}(q(k\tau)), k\tau)}{k_{B}(\gamma T - T)})$$ Note that since the biases are only added on integer values of CV, $V(\vec{s}(q(k\tau)), k\tau)=W_{0}$ at where the biases are added. (Note that $V(\vec{s}(q(k\tau)), k\tau)$ is approximately a Dirac delta function.) Therefore, with $W_{0}=0.5\;k_{B}T$ and $T=298 \;\text{K}$, we have $$s_{eff}=\exp(-\frac{0.5 k_{B}T}{k_{B}(\gamma T-T)})=\exp(-\frac{0.5}{\gamma - 1})$$As we specified `wl-scale` as 0.8 in GROMACS, we have $$0.8 = \exp(-\frac{0.5}{\gamma -1}) \Rightarrow \gamma = 1 - \frac{0.5}{\ln 0.8} \sim 3.24 $$ Since the assumption is very likely to be valid, $s_{eff}$ and $\gamma$ might still not be comparable in this case. However, we should also note that no matter what values of bias factor we use, the results from the two simulations should be similar and comparable. The only difference might just lie in the speed of convergence. For now, as we just want to test the validity of well-tempered metadynamics, using any values of bias factor should be fine. 
- Command
With the same `.tpr` file as the one used in Simulation 1, we can simply execute the following command to run the simulation:
`gmx mdrun -s sys1.tpr -x sys1.xtc -c sys1_output.gro -e sys1.edr -dhdl sys1_dhdl.xvg -g sys1.log -plumed`
- As a result, it took about 18.2 minutes to finish the simulation.

### 3. Comparison of the results between the simulations
- The final histogram
The final counts of Simulation 1 are:
  ```
              MC-lambda information
   N   VdwL    Count   G(in kT)  dG(in kT)
   1  0.000    33132    0.00000    0.16365
   2  0.200    34003    0.16365   -0.08816
   3  0.400    34266    0.07549   -0.77683
   4  0.600    35881   -0.70134   -1.85262 <<
   5  0.800    40319   -2.55397   -0.63869
   6  1.000    41075   -3.19266    0.00000
  ```
  while the final counts of Simulation 2 are:
  ```
              MC-lambda information
   N   VdwL    Count   G(in kT)  dG(in kT)
   1  0.000    34741  -22.20543   -0.12819
   2  0.200    33911  -22.33362   -0.06328
   3  0.400    34300  -22.39690   -0.65022 <<
   4  0.600    38565  -23.04712   -1.34964
   5  0.800    51555  -24.39676   -0.82782
   6  1.000    56928  -25.22458    0.00000
  ```
  Plotting the data above, we can get a histogram of Simulation (left) and Simulation 2 (right) as shown below. Surprisingly, the histogram of Simulation 2 is not as flat as the one of Simulation 1. This might be a matter of the choice of the bias factor. Further investigation is required to leverage the advantages of MetaD-EXE. 

<center><img src=https://i.imgur.com/nO8Spvt.png width=345><img src=https://i.imgur.com/oEWuuK4.png width=345></center>

- Exploration of state as a function of time
According to the information documented in the output `.log` file, in Simulation 1, the weights were quickly equilibrated at 0.628 ns (which only required about 2 minutes) even if a stricter criterion is applied (`weight-equil-wl-delta = 0.001`). As shown below, even if the histogram produced by Simulation 2 is not as flat as the one produced by Simulation 1, the system was able to sample all the states very frequently in both simulations, which should, therefore, be able to estimate the free energy difference accurately. Note that there is no weight equilibration in MetaD-EXE, since the weights were not Wang-Landau weights but Gaussian biasing potentials and the Wang-Landau were not used. 

<center><img src=https://i.imgur.com/aLwVwRj.png width=345><img src=https://i.imgur.com/cqlAKV4.png width=345></center>

- Free energy difference 
Similarly, we calculate the free energy difference from both simulations. The following is the results of free energy calculation from Simulation 1:
  ```
  ====== Results ======
  Statistical inefficiency of dHdl: 1.2748584747314453
  Statistical inefficiency of u_nk: 1.0

  TI: -3.1649716818793383 +/- 0.1713066178152106 kT
  BAR: -3.261757345786177 +/- unknown kT
  MBAR: -3.1652764821102064 +/- 0.1313865663349294 kT
  ```
  On the other hand, the following is the results from Simulation 2:
  ```
  ====== Results ======
  Statistical inefficiency of dHdl: 1.381946325302124
  Statistical inefficiency of u_nk: 1.0

  TI: -2.824904066409546 +/- 0.19319919579630265 kT
  BAR: -3.0584656008649795 +/- unknown kT
  MBAR: -3.0656459281787907 +/- 0.12837358357094564 kT
  ```
  Given the standard deviation of the values presented above, the results of the two simulations are statistically consistent with each other.
- Comparison of free energy calculations across different tests
Here we compare the free energy difference (units: kT) calculated from different simulations across different tests (Note: T1S1 means Simulation 1 in Test 1):


| -    | T1S1            | T1S2                 | T2S1                      | T2S2               | T3S1                      | T3S2                    |
| ---- | --------------- | -------------------- | ------------------------- | ------------------ | ------------------------- | ----------------------- |
| Type | EXE (0 weights) | MetaD-EXE (0 height) | EXE (updating $\Delta w$) | standard MetaD-EXE | EXE (updating $\Delta w$) | well-tempered MetaD-EXE |
| TI   | $-3.400 \pm 0.504$                | $-2.588 \pm 0.300$                     | $-5.850 \pm 0.347$                         | $-5.028 \pm 0.299$                   | $-3.165 \pm 0.171$                          | $-2.825 \pm 0.193$                       |
| BAR  | $-3.296$                | $-2.756$                     | $-3.760$                          | $-3.716$                   | $-3.262$                          | $-3.058$                        |
| MBAR     | $-3.270 \pm 0.233$                | $-2.968 \pm 0.202$                    | $-2.484 \pm 0.115$                         | $-3.012 \pm 0.125$                   |  $-3.165 \pm 0.131$                         | $-3.066 \pm 0.128$                       |
- Overlap matrix
If the sampling is sufficient, the overlap matrix should be at least tridiagonal. As shown below, both matrices meet this requirement and the overlap between states is significant.
<center><img src=https://i.imgur.com/QVFX82o.png width=345><img src=https://i.imgur.com/yUs4mLI.png width=345></center>


