# Test 1: A sanity check of alchemical metadynamics
###### tags: `MetaD-EXE-TestSys` `TestSystem1`

As mentioned, we fix the weights at 0 in the expanded ensemble (Simulation 1) and use `HEIGHT` in the alchemical metadynamics (Simulation 2) in the first test such that the simulations of both cases are not biased and should generate similar results. 

###th weights fixed at 0
- Path in the repository: `MetaD_EXE_TestSys/System1/Test_1/EXE_fixed`
- All the options related to Wang-Landau algorithm are turned off.
- 5 ns of simulation at 298 K. (Took about 15 minutes as a result.)
- 6 states are adopted, including 1 coupled state and 5 states for decoupling the van der Waals interactions. We don't need to decoupling electrostatic interactions here since there are no charges in the system.
- Content of the parameter file `sys1_expanded.mdp`
    ```
    ; Run control
    integrator               = md-vv
    tinit                    = 0
    dt                       = 0.002
    nsteps                   = 2500000  ; 5 ns
    comm-mode                = Linear
    nstcomm                  = 1

    ; Output control
    nstlog                   = 1000
    nstcalcenergy            = 1
    nstenergy                = 1000
    nstxout-compressed       = 1000

    ; Neighborsearching and short-range nonbonded interactions
    nstlist                  = 10
    ns_type                  = grid
    pbc                      = xyz
    rlist                    = 1.0

    ; Electrostatics
    cutoff-scheme		     = verlet
    coulombtype              = PME
    coulomb-modifier	     = Potential-shift-Verlet
    rcoulomb-switch          = 0.89
    rcoulomb                 = 0.9

    ; van der Waals
    vdw-type                 = Cut-off
    vdw-modifier             = Potential-switch
    rvdw-switch              = 0.85
    rvdw                     = 0.9

    ; Apply long range dispersion corrections for Energy and Pressure 
    DispCorr                 = AllEnerPres

    ; Spacing for the PME/PPPM FFT grid
    fourierspacing           = 0.10

    ; EWALD/PME/PPPM parameters
    fourier_nx               = 0
    fourier_ny               = 0
    fourier_nz               = 0
    pme_order                = 4
    ewald_rtol               = 1e-05
    ewald_geometry           = 3d
    epsilon_surface          = 0

    ; Temperature coupling
    tcoupl                   = v-rescale
    nsttcouple               = 1
    tc_grps                  = System
    tau_t                    = 0.5
    ref_t                    = 298

    ; Pressure coupling is on for NPT
    pcoupl                   = no

    ; refcoord_scaling should do nothing since there are no position restraints.

    gen_vel                  = yes
    gen-temp                 = 298
    gen-seed                 = 6722267; need to randomize the seed each time.

    ; options for bonds
    constraints              = h-bonds  ; we only have C-H bonds here

    ; Type of constraint algorithm
    constraint-algorithm     = lincs
    continuation             = no

    ; Highest order in the expansion of the constraint coupling matrix
    lincs-order              = 12
    lincs-iter               = 2

    ; Free energy calculation
    free_energy              = expanded
    calc-lambda-neighbors    = -1
    sc-alpha                 = 0.5
    couple-moltype           = Ar
    couple-lambda0           = vdw-q
    couple-lambda1           = none
    couple-intramol          = yes
    init-lambda-state        = 0

    nstdhdl                  = 1000
    dhdl-print-energy        = total

    ; Seed for Monte Carlo in lambda space
    lmc-seed                 = 1000
    lmc-gibbsdelta           = -1
    lmc-forced-nstart        = 0
    symmetrized-transition-matrix = yes
    nst-transition-matrix    = 100000
    ;wl-scale                 = 0.8
    ;wl-ratio                 = 0.6 ; keep this low, because the generations are short
    ;init-wl-delta            = 0.5 ; '20' to start, read from the logfile for restarts.

    ; expanded ensemble variables
    nstexpanded              = 10
    lmc-stats                = no
    lmc-move                 = metropolized-gibbs
    ;lmc-weights-equil        = wl-delta
    ;weight-equil-wl-delta    = 0.0001

    ; lambda-states          = 1      2      3      4      5      6      
    vdw-lambdas              = 0.00   0.20   0.40   0.60   0.80   1.00   
    ```
- Commands
    - `gmx grompp -f sys1_expanded.mdp -c sys1.gro -p sys1.top -o sys1.tpr -maxwarn 1`
    - `gmx mdrun -s sys1.tpr -x sys1.xtc -c sys1_output.gro -e sys1.edr -dhdl sys1_dhdl.xvg -g sys1.log`
- Note that the following warning would occur during the execution of `gmx grompp` if GROMACS 2020.1 is used (This warning is not present if GROMACS 2018.1 is used.):
    ```
    The GROMOS force fields have been parametrized with a physically
      incorrect multiple-time-stepping scheme for a twin-range cut-off. When
      used with a single-range cut-off (or a correct Trotter
      multiple-time-stepping scheme), physical properties, such as the density,
      might differ from the intended values. Since there are researchers
      actively working on validating GROMOS with modern integrators we have not
      yet removed the GROMOS force fields, but you should be aware of these
      issues and check if molecules in your system are affected before
      proceeding. Further information is available at
      https://redmine.gromacs.org/issues/2884 , and a longer explanation of our
      decision to remove physically incorrect algorithms can be found at
      https://doi.org/10.26434/chemrxiv.11474583.v1 .
    ```
- As a result, it took about 16.5 minutes to finish the simulation. 

### 2. Simulation 2: Alchemical metadynamics with `HEIGHT` being 0
- Path in the repository: `MetaD_EXE_TestSys/System1/Test_1/MetaD_EXE`
- The current implementation requires the expanded ensemble options remain on. Therefore, we use the sample `.mdp` file (hence the same `.tpr` file) as used in Simulation 1. The only difference is that we need a PLUMED input file here to activate alchemical metadynamics.
- Specifically, the PLUMED input file is shown as follows:
  ```
  lambda: EXTRACV NAME=lambda
  
  METAD ...
  ARG=lambda
  SIGMA=0.01     # small SIGMA ensure that the Gaussian approaximate a delta function
  HEIGHT=0       # In this case, the wegiths in EXE_fixed are fixed, meaning no biasing potentials added
  PACE=10        # should be equal to nstexpanded
  GRID_MIN=0     # index of alchemical states starts from 0
  GRID_MAX=5     # we have 6 states in total
  GRID_SPACING=1 # so that the values of CV should be 0, 1, 2, 3, 4, 5
  LABEL=metad    # it's not clear how GRID parameters will have influences here
  FILE=HILLS_LAMBDA
  ... METAD

  PRINT STRIDE=10 ARG=lambda,metad.bias FILE=COLVAR
  ```
- Note that in this test system, we only scale the van der Waals interaction with the following vector: $[0,\;0.2,\;0.4,\;0.6,\;0.8,\;1.0]$. Since the spacing in the values of $\lambda_{vdw}$ between neighboring state i constant here, one small enough `SIGMA` should be able to ensure the similarly between the Gaussian biasing potential annd the delta function. Specifically, with `SIGMA` as 0.01 in this case, the addition at a neighboring state would be negligible:$$W(t)\cdot \exp\left[-\sum_{i=1}^{d} \frac{\left(s_{g,i}−s_i(t)\right)^2}{2\sigma^2_i}\right] = W(t)\cdot \exp\left[-\frac{\left(0.2\right)^2}{2\cdot0.01^2}\right] = W(t)\cdot e^{-200} $$
- Note that it is recommended to specify parameters related to "GRID" in the PLUMEd input file, including `GRID_MIN`, `GRID_MAX`, and `GRID_SPACING`. According to [the documentation of PLUMED](https://www.plumed.org/doc-v2.6/user-doc/html/_m_e_t_a_d.html), in the simplest possible implementation of a metadynamics calculation (without `GRID_*` paramters), the expense of a metadynamics calculation increases with the length of the simulation, since one has to, at every step, evaluate the values of a larger and larger number of Gaussian kernels. To avoid this issue, we store the bias on a grid. As a comparison, with `GRID_*` parameters, it takes about 8.5 hours to finish the simulation, while it takes about only 15 minutes if `GRID_*` parameters are specified. Such a difference is generally case-specific.
- Command 
With the same `.tpr` file as Simulation 1, execute `gmx mdrun -s sys1.tpr -x sys1.xtc -c sys1_output.gro -e sys1.edr -dhdl sys1_dhdl.xvg -g sys1.log -plumed`.
- As a result, it took about 18.4 minutes to finish the simulation.

### 3. Comparison of the results between the simulations
- The final histogram 
  According to the `.log` file, the final counts of Simulation 1 is:
  ```
              MC-lambda information
  N   VdwL    Count   G(in kT)  dG(in kT)
  1  0.000     5743    0.00000    0.00000
  2  0.200     4873    0.00000    0.00000
  3  0.400     5299    0.00000    0.00000
  4  0.600    11119    0.00000    0.00000
  5  0.800    76461    0.00000    0.00000
  6  1.000   146505    0.00000    0.00000 <<
  ```
  And the final counts of Simulation 2 is:

  ```
  MC-lambda information
  N   VdwL    Count   G(in kT)  dG(in kT)
  1  0.000     5546    0.00000   -0.00000
  2  0.200     4817   -0.00000    0.00000
  3  0.400     5235   -0.00000    0.00000 <<
  4  0.600    11241   -0.00000    0.00000
  5  0.800    76502   -0.00000    0.00000
  6  1.000   146659   -0.00000    0.00000
  ```
  Plotting the data above, we can get a histogram of Simultion 1 (left) and 2 (right) as shown below. Apparently, the final counts of both simulations are pretty similar (hence the histogram).Since no weights were added in both simulations, the histograms were not flattened, but certainly, the system was still able to sample all the intermediate states.
    <center><img src=https://i.imgur.com/kPR7nND.png width=330><img src=https://i.imgur.com/v3gj80O.png width=330></center>
    
- Exploration of state as a function of time
As shown below, even if the weights/biases are 0, 6 intermediate states are enough for the system to sample the coupled and uncoupled state back and forth for multiple times in a single simulation. Again, both plots from different simulations exhibit similar patterns.
<center><img src=https://i.imgur.com/OeplLSR.png width=330><img src=https://i.imgur.com/f3bAIxj.png width=330></center>

- Data analysis using `COLVAR`
  Note that in addition to the `.log` file, we can also use PLUMED output file, `COLVAR` to plot the histogram and the state as a function of time as shown above. As a result, the figures obtained from the `COLVAR` file are exactly the same as the ones generated from the `.log` file. (Note that the time step in `COLVAR` is 100 smaller than the one in the `.log` file. This does not influence the result of the histogram, but we have to adopt the data point every 100 time frames if we want to reproduce state as a function of time based on the `.log` file. Currently the figure generated from `COLVAR` in the repository adopted all the data points.) 
- Free energy difference
Lastly, we compare the energy differences between the coupled and the uncoupled state calculated from Simulation 1 and Simulation 2. The following are the results from Simulation 1:
  ```
  ====== Results ======
  Statistical inefficiency of dHdl: 1.1017882823944092
  Statistical inefficiency of u_nk: 1.0
  
  TI: -3.399674527732527 +/- 0.5036968922133107 kT
  BAR: -3.296481230788155 +/- unknown kT
  MBAR: -3.2702770673303796 +/- 0.2334182069657454 kT
  ```
  Typically, when running metadynamics, we can use the PLUMED method `sum_hills` (`lumed sum_hills --hills HILLS_LAMBDA`) to add up all th biasing potential to get the free energy profile (as well as the free energy difference). However, this method won't work in Simulation 2 in our case here, since there was no biasing potential added. Therefore, we analyze the `.dhdl` file instead and the results are shown as follows: 
  ```
  ====== Results ======
  Statistical inefficiency of dHdl: 1.0295928716659546
  Statistical inefficiency of u_nk: 1.0

  TI: -2.5880824249128374 +/- 0.3005642544961182 kT
  BAR: -2.756222320576275 +/- unknown kT
  MBAR: -2.9676426988695743 +/- 0.20164515882905815 kT
  ```
  As shown in the results above, there was a difference of 0.35 kT between results of the two simulations analyzed by MBAR. Note that the uncertainty is somehow large but the results are still statistically consistent as the difference between the results obtained by same method based on different simulations are roughtly around the standard deviation. The uncertainty is large here because of the infrequency of visiting the first state. If the simulation is extended such that we have sufficient samples for all intermediate states (note that the counts in state 1 will still be significantly less than the counts in state 6.), then the uncertainy will be smaller.