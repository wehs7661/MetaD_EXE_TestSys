# Test systems for the development of MetaD-EXE sampling method

###### tags: `MetaD-EXE-TestSys`
This is a documentation for the details of the test systems preparation and the data analsysis of the corresponding simulations for the developement of alchemical metadynmics (MetaD-EXE). Except that the Test system 1 was prepared using GROMACS 2018.1 (which should have no influence on the results), all other preparations and the simulations were performed using GROMACS 2020.1 or 2020.2. All the files relevant to this document are hosted in [MetaD_EXE_TestSys](https://github.com/wehs7661/MetaD_EXE_TestSys.git) on GitHub.

## Equivalence between expanded ensemble (EXE) and alchemical metadynamics (MetaD-EXE)
Alchemical metadynamics biases the alchemical variable as a configurational collective variable. In the case that the Guassian biasing potentials added to the alchemical intermediate states are very narrow (`SIGMA` is almost 0)such that they approximate Dirac delta function, alchemical metadynamics is almost equivalent to expanded ensemble with non-fixed weights. (We will address the differences between the two later.) This characteristic is one of the important benchmarks that we can use to compare MetaD-EXE with EXE to ensure reasonable performance and robustness of MetaD-EXE along the way of developing it. In this specific case that they are equivalent, some of the simulation parameters defined in the PLUMED input file are related to the parameters in the GROMACS `.mdp` file. Specifically,
- `PACE` in the PLUMED input file (stride for adding Gaussian biasing potentials) is equivalent to `nstexpanded` in the `.mdp` file in GROMACS (stride for propose a move between alchemical states). Note that in an expanded ensemble, the weight a certain state (either the original state or the proposed state) changes whenever a move is proposed (no matter if the move is acceptd). If the move is accept, the proposed state changes, otherwise the weight of the original state changes. However, we should also note that in metadynamics, in effect, the move is proposed every step, while the move is proposed every `nstexpanded` in an expanded ensemble. Therefore, `PACE` and `nstexpanded` are only equivalent to each other in terms of the stride of changing the the weights of alchemical states. 
    - **Question**: In alchemical metadynamics, does the moves between different alchemical states based on MD simulations (just like biasing ordinary confomrational collective variables) or MC simulations (just like expanded ensemble)? If they are based on MC simulations, what is the frequency of proposing a move? Also, does it make more sense that we treat the alchemical variable as other conformational collective variables such that we decide whether the system should move to a new states according to the "effective force" based on the potential energy difference between the neighboring state? If the moves are based on MD simulations, then what is the effective frequency of proposing the move? (I think it should be 1 step but I want to make sure.)
    - **Answer**: State changes are via MC at frenquency `nstexpandd`. PLUMED does only accumulate the weights, the change of states is done identically to expanded ensemble. Changing the alchemical states through MD simulations is actually lambda dynamics. We decided to focus on MC first in an earlier meeting. Specifically, 
        - In the expanded ensemble simulation, `nstexpanded` does two things. One is proposing a new alchemical state, the other is changing the weights of either the current state (move rejected) or the proposed state (move accepted).
        - In the alchemical metadynamics, `nstexpanded` is only used for changing the state. The frequency of adjusting the weights is not `nstexpanded` but `PACE`. This is one of the reason that we want to specify both parameters in the current implementation. The behavior of `nstexpanded` can be easily modified by a if statement in the patch of PLUMED, which replaces the corresponding part of the code in GROMACS.
        - As shown above, `nstexpanded` and `PACE` are not exactly equivalent, but the results from different simulations (for example, Simulation 1 and Simulation 2 in Test 1 and Test 2 in Test system 1) should be comparable if they are set to the same values. 
        - Therefore, in the past, we use the Wang-Landau algorithm to adjust the weights of alchemical states, while now what we are trying to do is to develop a method that also uses MC simulation to switch states as in expanded ensemble but uses metadynamics to change the weights of the states.
- `HEIGHT` in the PLUMED input file (the initial height of the Gaussian biasing potentials) is equivalent to `init-wl-delta` (the initial value of the Wang-Landau incrementor) in the GROMACS `.mdp` file. Note, however, this is true only if the initial Wang-Landau weights is a zero vector. Also note that adding a Gaussian of height $h$ to an alchemical state is equivalent to *substracting* the Wang-Landau weight of that state by $h$ (so the probability of staying at the original place decreases), where $h=h(t)$ is the height of the Gaussian/value of the WL incrementor at time $t$. 
- `SIGMA` specifies the width of the Gaussian biasing potential in PLUMED, but there is no parameters analogous to it in expanded ensemble. (Or, expanded ensemble is mostly equivalent to metadynamics if `SIGMA` is 0.) Sine in MetaD-EE, we onl want to add the bias to one state without influencing the weights of any other states, in the current implementation of MetaD-EE, we use small `SIGMA` to make sure that the addition of the bias to the neighbor states is negligible. However, one thing we might have to deal with in the future is that the spacing in the value of alchemical variables ($\lambda_{vdw}$, $\lambda_{coul}$ or $\lambda_{restr}$, ...etc.) of different states in different scaling region might be different, depending the number of states in that certain region. As a result, we might need to make `SIGMA` variable such that it ensures the Gaussians are narrow enough in all regions. Otherwise, we might need another method to add biases in MetaDEXE to circumvent this issue. 
    - **Comment**: There is no need to have $\lambda$-dependent `SIGMA` as long as we want it to be essentially a delta function - we can just choose the `SIGMA` that is small enough for all the scaling regions. If we want to have `SIGMA` becoming larger, such that neighboring states are getting contribution, then a $\lambda$-dependent `SIGMA` could be necessary. 
- `wl-scale` in the GROMACS `.mdp` file controls how fast the Wang-Landau decreases once the histogram is considered flat. Therefore, expanded ensemble with `wl-scale=1` can be analogized to standard alchemical metadynamics, in which the height of the Gaussian biasing potential is constant. On the other hand, if `wl-scale` is smaller than 1, the expanded ensemble corresponds to well-tempered alchemical metadynamics.
- In PLUMED/metadynamics, `BIASFACTOR` is used to control the decreasing of the height of the Gaussians and therefore is similar to `wl-scale` in expanded ensemble. Specifically, the height of the Gaussians $W(k\tau)$ as a function of time ($t=k\tau$) and the bias factor $\gamma$ can be expressed as:
$$\gamma = \frac{T + \Delta T}{T},\;W(k\tau)=W_{0} \exp (-\frac{V(\vec{s}(q(k\tau)), k\tau)}{k_{B}\Delta T})$$
Therefore, the exponential term of $W(k\tau)$ can be regarded as the effective scale factor $s_{eff}$ in metadynamics. Practically, we control $\Delta T$ by specifying the value of $\gamma$, so here we express $s_{eff}$ as a function of $\gamma$ instead of $\Delta T$:
$$s_{eff} = \exp (-\frac{V(\vec{s}(q(k\tau)), k\tau)}{k_{B}(\gamma T - T)})$$ where $T$ is the simulation temperature. However, we should note that $s$ and $s_{eff}$ are analogous but not equivalent to each other, since the the height of the Gaussians is updated periodically, while the Wang-Landau incrementor is only updated when the histogram is considered flat and is therefore non-periodic. 

## Test system 1: An argon atom in a water box
As a system containing only 661 atoms, Test system 1 serves as a simple toy model for us to examine the functionalities of MetaD-EXE in the easiest way. Here, we take advantages of the equivalence between expanded ensemble and alchemical metadynamics. Specifically, in the first test, we compare the expanded ensemble with weights fixed at 0 with standard alchemical metadynamics. Since the weights are 0 throught the expanded ensemble simulation, the results should be similar to what we get from the standard metadynamics with `HEIGHT` being 0. Then, in the second test and the third test, we compare expanded ensemble with updating weights with standard MetaD-EXE and well-tempered MetaD-EXE, respeictively. The following table summarizes these three system:



| -                | Test 1             | Test 2                                           | Test 3                             |
| ---------------- | ------------------ | ------------------------------------------------ | ---------------------------------- |
| Type of EXE in Simulation 1      | Weights fixed at 0 (no biasing potential) | Weights updated by the WL algorithm                                 | Weights updated by the WL algorithm                  |
| Type of Meta-EXE in Simulation 2| standard           | standard                                         | well-tempered                      |
| Parameters       | `HEIGHT = 0`       | `HEIGHT` = `init-wl-delta`, `wl-scale` =0.999999 | `HEIGHT` = `init-wl-delta`, `wl-scale` = 0.8, `BIASFACTOR` = ? |

Below we start with the preparation of the simulation input files for all these tests. All the input files can be found in `Prep/Final_inputs`.

### 1. Preparation of the input files 
- Initial configuration:`sys1_init.gro`
    - The content of the file
        ```
        An argon in a water box
            1
            1Ar      Ar   1   0.500   0.500   0.500
        ```
    - The coordinates were decided arbitrarily.
- Construction of the box: `sys1_box.gro`
    - Command `gmx editconf -f sys1.gro -o test.gro -bt cubic -d 1 -c`
    - The content of the file
        ```
        An argon in a water box
        1
        1Ar      Ar    1   1.000   1.000   1.000
       2.00000   2.00000   2.00000
       ```
- Topology preparation: `sys1.top`
    - Adopted forcefield: GROMOS54a7
    - Adopted water model: SPC model
    - Changed the name of the `[ moleculetype ]` of the argon from `Other` to `Ar`. (Also change the name shown in `[ system ]` accordingly.)
    - Command: `gmx pdb2gmx -f sys1_box.gro -o sys1_top.gro -p sys1.top`
    - Note that the output `.gro` file, `sys1_top.gro` is actually exactly the same as `sys1_box.gro`.
    - Content of `sys1.top`:
        ```
        ;
        ;	File 'sys1.top' was generated
        ;	By user: wei-tse (1000)
        ;	On host: castlepeak
        ;	At date: Mon Mar  9 12:47:08 2020
        ;
        ;	This is a standalone topology file
        ;
        ;	Created by:
        ;	                    :-) GROMACS - gmx pdb2gmx, 2018.1 (-:
        ;	
        ;	Executable:   /usr/bin/gmx
        ;	Data prefix:  /usr
        ;	Working dir:  /home/wei-tse/Documents/MetaD_EXE/test_systems/sys1
        ;	Command line:
        ;	  gmx pdb2gmx -f sys1_box.gro -o sys1_top.gro -p sys1.top
        ;	Force field was read from the standard GROMACS share directory.
        ;

        ; Include forcefield parameters
        #include "gromos54a7.ff/forcefield.itp"

        [ moleculetype ]
        ; Name            nrexcl
        Ar               3

        [ atoms ]
        ;   nr       type  resnr residue  atom   cgnr     charge       mass  typeB    chargeB      massB
        ; residue   1 Ar  rtp AR   q  0.0
             1         AR      1     Ar     Ar      1          0     39.948   ; qtot 0

        ; Include Position restraint file
        #ifdef POSRES
        #include "posre.itp"
        #endif

        ; Include water topology
        #include "gromos54a7.ff/spc.itp"

        #ifdef POSRES_WATER
        ; Position restraint for each water oxygen
        [ position_restraints ]
        ;  i funct       fcx        fcy        fcz
           1    1       1000       1000       1000
        #endif

        ; Include topology for ions
        #include "gromos54a7.ff/ions.itp"

        [ system ]
        ; Name
        An argon in a water box

        [ molecules ]
        ; Compound        #mols
        Ar               1
        ```

- Solvation of the system: `sys1_sol.gro`
    - Command: `gmx solvate -cp sys1_top.gro -p sys1.top -o sys1_sol.gro -cs`
    - Used VMD to check the structure.

- Energy minimization
    - Commands 
        - `gmx grompp -f em.mdp -c ../sys1_sol.gro -p ../sys1.top -o sys1_em.tpr`
        - `gmx mdrun -s sys1_em.tpr -o sys1_em.trr -c sys1_em.gro -g em.log -e em.edr`
    - STDOUT of `mdrun`:
        ```
        Steepest Descents converged to Fmax < 100 in 43 steps
        Potential Energy  = -9.7695146e+03
        Maximum force     =  9.9665489e+01 on atom 375
        Norm of force     =  2.9507223e+01
        ```
    - Content of `em.mdp`
        ```
        ; em.mdp - used as input into grompp to generate em.tpr
        ; All unspecified parameters adopt their own default values.

        ; Run Control
        integrator  = steep         ; Algorithm (steep = steepest descent minimization)
        nsteps      = 500000        ; (0) maximum number of steps to integrate or minimize

        ; Energy minnimization
        emtol       = 100.0        ; (10.0) Stop minimization when the maximum force < 100.0 kJ/mol/nm
        emstep      = 0.01          ; (0.01) [nm] Minimization step size

        ; Neighbor searching/Electrostatics/Van der Waals
        cutoff-scheme   = Verlet    ; Buffered neighbor searching
        nstlist         = 10        ; (10) Frequency to update the neighbor list and long range forces
        ns_type         = grid      ; Method to determine neighbor list (simple, grid)
        pbc             = xyz       ; Periodic Boundary Conditions in all 3 dimensions
        coulombtype     = PME       ; Treatment of long range electrostatic interactions
        rcoulomb        = 0.9       ; Short-range electrostatic cut-off
        rvdw            = 0.9       ; Short-range Van der Waals cut-off
        rlist           = 0.9
        ```
    - Note that the cut-off length (`rlist`) should be smaller than half of the shortest box vector. Instead of increase the box size, we changed `rlist` from the default (1.0 nm) to 0.9 nm.

- NVT Equilibration
  - Temperature: 298 K
  - Commands
      - `gmx grompp -f nvt_equil.mdp -c ../../EM/sys1_em.gro -p ../../sys1.top -o sys1_equil.tpr`
      - `gmx mdrun -s sys1_equil.tpr -o sys1_equil.trr -c sys1_equil.gro -g equil.log -e equil.edr`
  - It took about 41 seconds to finish this 200 ps of equilibration.
  - Content of `nvt_equil.mdp`
    ```
    ; Run control
    integrator               = md
    tinit                    = 0
    dt                       = 0.002
    nsteps                   = 100000  ; 200 ps
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
    cutoff-scheme         = verlet
    coulombtype              = PME
    coulomb-modifier     = Potential-shift-Verlet
    rcoulomb-switch          = 0.89
    rcoulomb                 = 0.9

    ; van der Waals
    vdw-type                 = Cut-off
    vdw-modifier             = Potential-switch
    rvdw-switch              = 0.85
    rvdw                     = 0.9

    ; Apply long-range dispersion corrections for Energy and Pressure 
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
    pcoupl                   = no   ; no pressure for NVT equilibration

    gen_vel                  = yes
    gen-temp                 = 298
    gen-seed                 = 6722267; need to randomize the seed each time.

    ; options for bonds
    constraints              = h-bonds  ; we only have C-H bonds here
    ; Type of constraint algorithm
    constraint-algorithm     = lincs
    ; Highest order in the expansion of the constraint coupling matrix
    lincs-order              = 12
    lincs-iter               = 2
    ```
    
- NPT equilibration
    - Temperature: 298 K
    - Commands
        - `gmx grompp -f npt_equil.mdp -c ../NVT/sys1_equil.gro -t ../NVT/state.cpt -p ../../sys1.top -o sys1_equil.tpr`
        - `gmx mdrun -s sys1_equil.tpr -o sys1_equil.trr -c sys1_equil.gro -g equil.log -e equil.edr`
    - Berendsen coupling was used.
    - It took about 48 seconds to finish this 200 ps of equilibration.

- A short MD simulation in an NPT ensemble 
    - Temperature: 298 K
    - Commands
        - `gmx grompp -f md.mdp -c ../Equil/NPT/sys1_equil.gro -p ../sys1.top -o sys1_md.tpr -t ../Equil/NPT/state.cpt`
        - `gmx mdrun -s sys1_md.tpr -o sys1_md.trr -c sys1_md.gro -g md.log -e md.edr`
    - Parrinello-Rahman coupling was used.
    - It took about 15 minutes 18 seconds to finish this 5 ns of production run. (So about 3 minutes per ns.)

- Extraction the configuration suitable for advanced sampling in an NVT ensemble
    - Commands
        - `gmx energy -f md.edr -s sys1_md.tpr -o volume.xvg` (Choose `15`: volume.)
        - `python gmx_plot2d.py -f MD/volume.xvg -x "Time (ps)" -y "Volume ($ nm^{3} $)" -t "Volume as a function of time" -n sys1_volume`
        - `gmx trjconv -s sys1_md.tpr -f traj_comp.xtc -o sys1.gro -dump 3236` (Choose `0`: system)
    - Volume as a function of time
    <center><img src=https://i.imgur.com/WgK4YzM.png width=500></center>
    - As a result, the average volume over the whole simulation is about 6.785776 $nm^{3}$. The time frame at which the volume is closest to this value is 3.236 ns (volume: 6.785793 $nm^{3}$), so we dumped the configuration at this time frame from the MD trajectory to make it the input to advanced sampling simulations in an NVT ensemble. 


### 2. Test 1: A sanity check of alchemical metadynamics
As mentioned above, we fix the weights at 0 in the expanded ensemble (Simulation 1) and use `HEIGHT` in the alchemical metadynamics (Simulation 2) in the first test such that the simulations of both cases are not biased and should generate similar results. 

#### 2-1. Simulation 1: expanded ensemble simulation with weights fixed at 0
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

#### 2-2. Simulation 2: Alchemical metadynamics with `HEIGHT` being 0
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
- Command </br>
With the same `.tpr` file as Simulation 1, execute `gmx mdrun -s sys1.tpr -x sys1.xtc -c sys1_output.gro -e sys1.edr -dhdl sys1_dhdl.xvg -g sys1.log -plumed`.
- As a result, it took about 18.4 minutes to finish the simulation.

#### 2-3. Comparison of the results between the simulations
- The final histogram </br>
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
    
- Exploration of state as a function of time</br>
As shown below, even if the weights/biases are 0, 6 intermediate states are enough for the system to sample the coupled and uncoupled state back and forth for multiple times in a single simulation. Again, both plots from different simulations exhibit similar patterns.
<center><img src=https://i.imgur.com/OeplLSR.png width=330><img src=https://i.imgur.com/f3bAIxj.png width=330></center>

- Data analysis using `COLVAR`</br>
  Note that in addition to the `.log` file, we can also use PLUMED output file, `COLVAR` to plot the histogram and the state as a function of time as shown above. As a result, the figures obtained from the `COLVAR` file are exactly the same as the ones generated from the `.log` file. (Note that the time step in `COLVAR` is 100 smaller than the one in the `.log` file. This does not influence the result of the histogram, but we have to adopt the data point every 100 time frames if we want to reproduce state as a function of time based on the `.log` file. Currently the figure generated from `COLVAR` in the repository adopted all the data points.) 
- Free energy difference</br>
Lasly, we compare the energy differences between the coupled and the uncoupled state calculated from Simulation 1 and Simulation 2. The following are the results from Simulation 1:
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

### 3. Test 2: Examination of biasing potentials in standard MetaD-EXE 
As mentioned above, in the second test, we want to really bias the alchemical variable with the standard metadynamics, in which the height of the Gaussian biasing potential remain constant throughout the simulation. To compare the results of this simulation, we specify `init-wl-delta` used in the expanded ensemble (Simulation 1) as the same value of `HEIGHT` used in alchemical metadynamics (Simulation 2) and set `wl-scale = 1` in Simulation 1 to make the Wang-Landau incrementor a constant. With these parameters, the results obtained from the two simulations, including the final histogram, the state as a function of time and the free energy difference, should be similar. 

#### 3-1. Simulation 1: expanded ensemble simulation with updating weights (`wl-scale` $\sim$ 1)
- Path in the repository: `MetaD_EXE_TestSys/System1/Test_2/EXE_updating`
- In contrast to Simulation 1 in Test 1, all the options related to Wang-Landau algorithm should be turned on, including `lmc-stats = wang-landau` instead of `no`, `wl-scale`, `wl-ratio`, and `weight-equil-wl-delta`.
- Note that in GROMACS, `wl-scale` can be not exactly set as 1, so use set it as 0.999999 instead. This makes the Wang-Landau approximately remain the same even after 10000 updates ($0.999999^{10000} \sim 0.99005$). Note that since the Wang-Landau incrementor barely decreases, it will "never" reach the criteria of the weight equilibration, which is that $\Delta w < 0.01$ specified in the GROMACS `.mdp` file.
- Similarly, the simulation is conducted with exactly the same 6 alchemical states used previously at 298 K for 5 ns. (Check the `.mdp` file in the repository for more details.)
- Commands
    - `gmx grompp -f sys1_expanded.mdp -c sys1.gro -p sys1.top -o sys1.tpr -maxwarn 1`
    - `gmx mdrun -s sys1.tpr -x sys1.xtc -c sys1.gro -e sys1.edr -dhdl sys1_dhdl.xvg -g sys1.log`
- As a result, it took about 16.3 minutes to finish the simulation.
    
#### 3-2. Simulation 2: Standard alchemical metadynamics (constant Gaussian height)
- Path in the repository: `MetaD_EXE_TestSys/System1/Test_2/MetaD_EXE`
- The PLUMED input file used in this simulation is shown as follows:
  ```
  lambda: EXTRACV NAME=lambda

  METAD ...
  ARG=lambda
  SIGMA=0.01     # small SIGMA ensure that the Gaussian approaximate a delta function
  HEIGHT=0.5     # should be equal to init-wl-delta in standard alchemical metadynamics
  PACE=10        # should be nstexpanded
  LABEL=metad    # it's not clear how GRID parameters will have influences here
  FILE=HILLS_LAMBDA
  ... METAD

  PRINT STRIDE=10 ARG=lambda,metad.bias FILE=COLVAR
  ```
  The only difference between the PLUMED input file used here and the one used previously in Simulation 2 in Test 1 is that now `HEIGHT` is non-zero and equal to `init-wl-delta` specified in the GROMACS `.mdp` file.
- Command
With exactly the same `.tpr` file as Simulation 1 in Test 2, execute `gmx mdrun -s sys1.tpr -x sys1.xtc -c sys1_output.gro -e sys1.edr -dhdl sys1_dhdl.xvg -g sys1.log -plumed`.
- As a reulst, it took about 18.2 minutes to finish the simulation if `GRID_*` parameters are used.

#### 3-3. Comparison of the results between the simulations
- The final histogram </br>
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
  However, we can stil check the final counts of the states of Simulation 2:
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
  As shown above, the weights esitmated by alchemical metadynamics ensure pretty flat histogram. In the current implementation, the weight of the first state was not shifted to 0 though, which is the problem we have to solve in the near future.
- Exploration of state as a function of time</br>
As shown below, the figure on the left is the result from Simulation 1, while the one on the right is the result from Simulation 2 (based on the `.log` file). All the states are well sampled in both simulations.
<center><img src=https://i.imgur.com/PyqenR1.png width=330><img src=https://i.imgur.com/QiJYqHN.png width=330></center> 

- Free energy difference </br>
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

- Overlap matrix</br>
If the sampling is sufficient, the overlap matrix should be at least tridiagonal. As shown below, both matrices meet this requirement and the overlap between states is significant. 
<center><img src=https://i.imgur.com/NCFypph.png width=330><img src=https://i.imgur.com/uCC98nd.png width=330></center> 




### 4. Test 3: Examination of biasing potentials in well-temeperd MetaD-EXE 
**Note: The content in this section has not been updated. (05.31)**
- In Test 2, the inital lambda weights are set to be 0. (Therefore, there is no need to specify `init-wl-delta` in the `.mdp` file.) The only difference from Test 1 is that instead of fixing the weights at 0, we used Wang-Landau algorithm to update the weights. After the histogram is flat, the simulation will automatically continue with fixed weights.
- 5 ns of simulation with 6 intermediate states at 298 K. (Took about 17 minutes).
- Specify options like 
    - `wl-scale = 0.8`
    - `wl-ratio = 0.8`
    - `init-wl-delta = 0.5`
    - `lmc-stats = wang-landau`
    - `weight-equil-wl-delta = 0.1`
    - Other parameters are all the same as the ones used in Test 1.
- The commands are exactly the same as the ones used in Test 1 and the same warning would occur. We similarly ignore the warning here.
- Results
    - The final histogram
    The data of the final histogram of the simulation is:
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
        As can be seen below, with updating weights added, the histogram is relatively flat than the one obtained in the previous simulation.
        <center><img src=https://i.imgur.com/nO8Spvt.png width=500></center>
        
    - Exploration of state as a function of time
    Accorindgly the to information documented in the output `.log` file, the weights were quickly equilibrated at 0.628 ns (which only required about 2 minutes) even if a stricter criteria is applied (`weight-equil-wl-delta = 0.001`). In addition, the system was able to sample all the states back and forth even more frequently than the previous simulation. The longest time required for the system to sample all the states is only 0.096 ns.


<center><img src=https://i.imgur.com/aLwVwRj.png width=500></center>





## Test system 2: a lactic acid in the water box
In the second test system, we want to compare the alchemical metadynamics with the existing methods for the calculation of the solvation free energy. The system of interest is a lactic acid in the water box, which has only one potential intramolecular hydrogen bond (between the hydrogen atom of the hydroxyl group and the oxygen atom of the carboxyl group). 

To calculate the solvation free energy with currently existing methods, we can either run a bunch of vanilla simulations at different values of the alchemical variable $\lambda$ or run an expanded ensemble simulation. In the tests here, we will specify `couple-intramol = no` to maintain the intramolecular hydrogen bond, which will make the system kinetically trapped at $\lambda=0$, the uncoupled alchemical state which is equivalent to the case of the lactic acid being in the vacuum. Specifically, in a water box (at $\lambda=1$), the lactic acid can form hydrogen bonds either internally or with the water molecules around, which leads to a lower energy barrier along the CV defined as the torsional angle. On the other hand, in vacuum ($\lambda=0$), only one intramolecular hydrogen bond can be formed, so the torsion remains trapped in a certain value. As will be shown below, expanded ensemble is sufficient to overcome the energy barrier, and the goal here, is to examine whether the introduction of metadynamics (hence alchemical metadynamics) can accelerate the process further.

<center>
<img src=https://i.imgur.com/WMOFDIg.png width=250><img src=https://i.imgur.com/IQmy1bn.png width=250>
</center>

Specifically, regarding this test system, the following tests will be performed (Note that Simulation 1 is the control group):


| -            | Test 1                                              | Test 2                                                       |
| ------------ | --------------------------------------------------- | ------------------------------------------------------------ |
| Simulaion 1  | Vanilla MD simulations at </br> different $\lambda$ values | Expanded ensemble with </br> updating weights                      |
| Simulation 2 | Standard alchemical metadynamics                    | Well-tempered </br> alchemical metadynamics                                   |
| Parameters   | `HEIGHT=0`                                          | `HEIGHT` = `init-wl-delta`</br>, `wl-scale` = 0.8, `BIASFACTOR`=? |



### 1. Preparation of the input files
- Initial configuration
  - As shown above, lactic acid has two enantiomers (stereoisomers that are non-superimposable mirror images), which are the L-form and D-form lactic acid. L-form lactic acid is the natural form which can be processed by human bodies, but it doesn't matter which form of lactic acid we use in our case.
  - The SDF structure file of the D-form of the lactic acid can be obtained from [Protein Data Bank](https://www.rcsb.org/ligand/LAC). Save the file as `sys1_init.sdf`
  - To convert the SDF file to a PDB file, execute:
    ```
    babel sys2_init.sdf sys2_init.pdb
    ```
    The execution of the command above requires Open Babel to be installed in advance. Open Babel can be installed by
    ```
    sudo apt install openbabel
    ```
- Topology preparation: `
  - Here we use Open Forcefield and OpenMM to prepare the system topology, and use ParmEd to convert the OpenMM topology to  GROMACS files (including `system.gro` file and `system.top` file). The process can be done by simply executing 
    ```
    python openff.py
    ```
  - `openff.py` is an adpatation of the example code provided by the [tutorial on Open Forcefield](https://github.com/openforcefield/openforcefield/blob/master/examples/using_smirnoff_in_amber_or_gromacs/convert_to_amber_gromacs.ipynb), whose content is as follows:
    ```Python
    from simtk.openmm.app import PDBFile
    from openforcefield.topology import Molecule, Topology
    from openforcefield.typing.engines.smirnoff import ForceField

    LAC = Molecule.from_smiles("C[C@@H](O)C(O)=O")

    # Obtain the OpenMM Topology object from the PDB file.
    pdbfile = PDBFile('sys2_init.pdb')
    omm_topology = pdbfile.topology

    # Create the Open Forcefield Topology.
    off_topology = Topology.from_openmm(omm_topology, unique_molecules=[LAC])

    # Load the "Parsley" force field.
    forcefield = ForceField('openff_unconstrained-1.0.0.offxml')
    omm_system = forcefield.create_openmm_system(off_topology)

    # convert OpenMM System to a ParmEd structure.
    parmed_structure = parmed.openmm.load_topology(omm_topology, omm_system, pdbfile.positions)

    # Export GROMACS files.
    parmed_structure.save('system.top', overwrite=True)
    parmed_structure.save('system.gro', overwrite=True)
    ```
  - Warnings (saved in `openff.log`):
    ```
    /home/wei-tse/anaconda3/lib/python3.7/site-packages/simtk/openmm/app/internal/pdbstructure.py:536: UserWarning: WARNING: duplicate atom (HETATM    2  C   LIG     1       0.185  -0.428   0.713  1.00  0.00           C  , HETATM    1  C   LIG     1      -0.123  -0.059  -0.715  1.00  0.00           C  )
    warnings.warn("WARNING: duplicate atom (%s, %s)" % (atom, old_atom._pdb_string(old_atom.serial_number, atom.alternate_location_indicator)))
    /home/wei-tse/anaconda3/lib/python3.7/site-packages/simtk/openmm/app/internal/pdbstructure.py:536: UserWarning: WARNING: duplicate atom (HETATM    3  C   LIG     1       1.353   0.421   1.218  1.00  0.00           C  , HETATM    2  C   LIG     1       0.185  -0.428   0.713  1.00  0.00           C  )
    warnings.warn("WARNING: duplicate atom (%s, %s)" % (atom, old_atom._pdb_string(old_atom.serial_number, atom.alternate_location_indicator)))
    /home/wei-tse/anaconda3/lib/python3.7/site-packages/simtk/openmm/app/internal/pdbstructure.py:536: UserWarning: WARNING: duplicate atom (HETATM    5  O   LIG     1      -0.964  -0.188   1.526  1.00  0.00           O  , HETATM    4  O   LIG     1      -1.216   0.365  -1.006  1.00  0.00           O  )
    warnings.warn("WARNING: duplicate atom (%s, %s)" % (atom, old_atom._pdb_string(old_atom.serial_number, atom.alternate_location_indicator)))
    /home/wei-tse/anaconda3/lib/python3.7/site-packages/simtk/openmm/app/internal/pdbstructure.py:536: UserWarning: WARNING: duplicate atom (HETATM    6  O   LIG     1       0.815  -0.202  -1.663  1.00  0.00           O  , HETATM    5  O   LIG     1      -0.964  -0.188   1.526  1.00  0.00           O  )
    warnings.warn("WARNING: duplicate atom (%s, %s)" % (atom, old_atom._pdb_string(old_atom.serial_number, atom.alternate_location_indicator)))
    /home/wei-tse/anaconda3/lib/python3.7/site-packages/simtk/openmm/app/internal/pdbstructure.py:536: UserWarning: WARNING: duplicate atom (HETATM    8  H   LIG     1       1.577   0.154   2.251  1.00  0.00           H  , HETATM    7  H   LIG     1       0.454  -1.483   0.765  1.00  0.00           H  )
    warnings.warn("WARNING: duplicate atom (%s, %s)" % (atom, old_atom._pdb_string(old_atom.serial_number, atom.alternate_location_indicator)))
    /home/wei-tse/anaconda3/lib/python3.7/site-packages/simtk/openmm/app/internal/pdbstructure.py:536: UserWarning: WARNING: duplicate atom (HETATM    9  H   LIG     1       2.230   0.239   0.597  1.00  0.00           H  , HETATM    8  H   LIG     1       1.577   0.154   2.251  1.00  0.00           H  )
    warnings.warn("WARNING: duplicate atom (%s, %s)" % (atom, old_atom._pdb_string(old_atom.serial_number, atom.alternate_location_indicator)))
    /home/wei-tse/anaconda3/lib/python3.7/site-packages/simtk/openmm/app/internal/pdbstructure.py:536: UserWarning: WARNING: duplicate atom (HETATM   10  H   LIG     1       1.084   1.476   1.165  1.00  0.00           H  , HETATM    9  H   LIG     1       2.230   0.239   0.597  1.00  0.00           H  )
    warnings.warn("WARNING: duplicate atom (%s, %s)" % (atom, old_atom._pdb_string(old_atom.serial_number, atom.alternate_location_indicator)))
    /home/wei-tse/anaconda3/lib/python3.7/site-packages/simtk/openmm/app/internal/pdbstructure.py:536: UserWarning: WARNING: duplicate atom (HETATM   11  H   LIG     1      -1.168   0.753   1.451  1.00  0.00           H  , HETATM   10  H   LIG     1       1.084   1.476   1.165  1.00  0.00           H  )
    warnings.warn("WARNING: duplicate atom (%s, %s)" % (atom, old_atom._pdb_string(old_atom.serial_number, atom.alternate_location_indicator)))
    /home/wei-tse/anaconda3/lib/python3.7/site-packages/simtk/openmm/app/internal/pdbstructure.py:536: UserWarning: WARNING: duplicate atom (HETATM   12  H   LIG     1       0.617   0.034  -2.579  1.00  0.00           H  , HETATM   11  H   LIG     1      -1.168   0.753   1.451  1.00  0.00           H  )
    warnings.warn("WARNING: duplicate atom (%s, %s)" % (atom, old_atom._pdb_string(old_atom.serial_number, atom.alternate_location_indicator)))
    Warning: OEAM1BCCELF10 charge assignment failed due to a known bug (toolkit issue #346). Downgrading to OEAM1BCC charge assignment for this molecule. More informationis available at https://github.com/openforcefield/openforcefield/issues/346
    ```
    
- Construction of the box: `sys2_box.gro`
  - Command: `gmx editconf -f system.gro -o sys2_box.gro -bt cubic -d 1 -c`
  - STDOUT:
    ```
    Read 12 atoms
    Volume: 0.206039 nm^3, corresponds to roughly 0 electrons
    No velocities found
        system size :  0.345  0.296  0.483 (nm)
        diameter    :  0.493               (nm)
        center      :  0.040  0.009  0.031 (nm)
        box vectors :  0.566  0.614  0.593 (nm)
        box angles  :  90.00  90.00  90.00 (degrees)
        box volume  :   0.21               (nm^3)
        shift       :  1.206  1.237  1.215 (nm)
    new center      :  1.246  1.246  1.246 (nm)
    new box vectors :  2.493  2.493  2.493 (nm)
    new box angles  :  90.00  90.00  90.00 (degrees)
    new box volume  :  15.49               (nm^3)
    ```
  - Note that `system.gro` is bascially the same (coordinates) as `sys2_init.pdb`.
- Solvation of the system: `sys2_sol.gro`
  - Command: `gmx solvate -cp sys2_box.gro -p system.top -o sys2_sol.gro -cs` 
  - STDOUT:
    ```
    Generating solvent configuration
    Will generate new solvent configuration of 2x2x2 boxes
    Solvent box contains 2151 atoms in 717 residues
    Removed 633 solvent atoms due to solvent-solvent overlap
    Removed 15 solvent atoms due to solute-solvent overlap
    Sorting configuration
    Found 1 molecule type:
        SOL (   3 atoms):   501 residues
    Generated solvent containing 1503 atoms in 501 residues
    Writing generated configuration to sys2_sol.gro

    Output configuration contains 1515 atoms in 502 residues
    Volume                 :     15.4865 (nm^3)
    Density                :     977.442 (g/l)
    Number of solvent molecules:    501

    Processing topology
    Adding line for 501 solvent molecules with resname (SOL) to topology file (system.top)

    Back Off! I just backed up system.top to ./#system.top.1#
    ``` 
   - Better off checking the structure in VMD.

- Modification of the topology file
  - To ensure that the atom types of the water molecules added and the ions to be added (if needed) can be recognized, we have to add the corresponding atom types in the topology file. In our case, since net charge of the system is 0 and we are not going to include any buffer solution, we only have to add the atom types relevant to the water molecules in the chosen force field.
  - Note that the output topology of Open Forcefield is an all-atom topology, which implies that we can only use an all-atom force field. Accordingly, here we choose AMBER99SB-ILDN force filed. (Note that it should be fine as long as the force field is all-atom.) 
  - An improper force field (like GROMOS54a7, which is an united-atom force field) might lead to bad contacts between atoms (i.e., the distance between atoms is too small), which results in large forces and numerical instability. When this is the case, one can often observe that in STDOUT of energy minimization, the maximum force is unreasonably large. And an `mdrun` command used for equilibrations will return an error like `step XXX: One or more water molecules can not be settled.`.
  - To include the `.itp` files in AMBER99SB-ILDN, first of all, add the following lines to `system.top`:
     ```
    ; Include water topology
    #include "amber99sb-ildn.ff/tip3p.itp"
     ```
  - To make the inclusion of the `.itp` files effective, we need to add all the atom types defined in the `tip3p.itp`. These atom types can be found in `/usr/share/gromacs/top/gromos54a7.ff/ffnonbonded.itp`. Specifically, append the following atom types to `[atomtypes]` directive of `system.top`:
     ```
     OW             8      16.00      0.0000  A    3.15061e-01    6.36386e-01
    HW             1      1.008      0.0000  A    0.00000e+00    0.00000e+00
     ```
  - For a more detailed description, please refer to [Preparation of the Inputs Files for Advanced Sampling Simulations - Part 1](https://hackmd.io/@WeiTseHsu/BJF0tBizU).
- Energy minimization:
   - From the topology file `system.top`, we can see that the net charge of the system is 0. In addition, we are not going to include any buffer solution in our case, so we don't need to add addition sodium or chloride ions to the system and can directly proceed the system to energy minimization.
   - In this step, we use exactly the same parameter file `em.mdp` as Test system 1.
   - Command:
     - `gmx grompp -f em.mdp -c ../sys2_sol.gro -p ../system.top -o sys2_em.tpr`
     - `gmx mdrun -s sys2_em.tpr -o sys2_em.trr -c sys2_em.gro -g em.log -e em.edr`
  - STDOUT of `mdrun`:
    ```
    Steepest Descents converged to Fmax < 100 in 2654 steps
    Potential Energy  = -2.3768379e+04
    Maximum force     =  9.9607666e+01 on atom 1
    Norm of force     =  1.0470232e+01
    ```
- NVT equilibration
  - Here we use exactly the same parameter file as `nvt_equil.mdp` used in the NVT equilibration Test system 1.
  - Temperature: 298 K
  - Commands
    - `gmx grompp -f nvt_equil.mdp -c ../../EM/sys2_em.gro -p ../../system.top -o sys2_equil.tpr`
    - `gmx mdrun -s sys2_equil.tpr -o sys2_equil.trr -c sys2_equil.gro -g equil.log -e equil.edr`
  - It took about 53 seconds to finish this 200 ps of equilibration.
- NPT equilibration
  - Similarly, here we use exactly the same parameter file as `npt_equil.mdp` used in the NPT equilibration of Test system 1.
  - Temperature: 298 K
  - Commands
    - `gmx grompp -f npt_equil.mdp -c ../NVT/sys2_equil.gro -t ../NVT/state.cpt -p ../../system.top -o sys2_equil.tpr`
    - `gmx mdrun -s sys2_equil.tpr -o sys2_equil.trr -c sys2_equil.gro -g equil.log -e equil.edr`
  - Berendsen coupling was used.
  - It took about 104 seconds to finish this 200 ps of equilibration.
- A short MD simulation in an NPT ensemble
  - Here, we use exactly the same parameter file as `md.mdp` used in the short MD simulation of Test system 1.
  - Temperature: 298 K.
  - Commands
    - `gmx grompp -f md.mdp -c ../Equil/NPT/sys2_equil.gro -p ../system.top -o sys2_md.tpr -t ../Equil/NPT/state.cpt`
    - `gmx mdrun -s sys2_md.tpr -o sys2_md.trr -c sys2_md.gro -g md.log -e md.edr`
  - Parrinello-Rahman coupling was used.
  - It took about 2 hours to finish this 5 ns of production run. (So about 24 minutes per ns.)
- Extraction the configuration suitable for advanced sampling in an NVT ensemble
  - Commands
    - `gmx energy -f md.edr -s sys2_md.tpr -o volume.xvg` 
    - `plot_2d -f volume.xvg -x "Time (ps)" -y "Volume ($nm^{3}$)" -t "Volume as a function of time" -n sys2_volume` This command is enabled by the installation of [`MolSci_analysis`](https://github.com/wehs7661/MolSci_analysis.git), which produces the following STDOUT:
      ```
      Data analysis of the file: volume.xvg
      =====================================
      Analyzing the file ...
      Plotting and saving figure ...
      The average of volume: 15.313 nm^{3}  (RMSF: 0.013 nm^{3}  max: 15.969 nm^{3} , min: 14.703 nm^{3} )      
      The maximum occurs at 1.6820 ns, while the minimum occurs at 2.7420 ns.
      The configuration at 0.468 ns has the volume (15.313675 nm^{3} ) that is cloest to the average volume. 
      ```
    - `gmx trjconv -s sys2_md.tpr -f traj_comp.xtc -o sys2.gro -dump 468` (Choose `0`: system)

  - Volume as a function of time
  - <center><img src=https://i.imgur.com/GKXYMZy.png width=500></center>
  - Like we did in the Test system 1, we dump the time frame at which the volume of configuration is closet to the average value. 
- Finally, in the folder `System_2/Prep`, execute the following commands to collect the files serving as the input files for Test 1 and Test 2:
  ```
  mkdir Final_inputs && cd Final_inputs
  cp ../MD/sys2.gro .
  cp ../system.top sys2.top
  ```

### 2. Test 1: Comparison between vanilla simulations and alchemical metadynamics
As mentioned above, Test 1 is more like a sanity as Test 1 of Test system 1. In Test 1 here, we run a series of vanilla MD simultions at different $\lambda$ values in Simulation 1. This simulation is analogous to Simulation 1 in Test 1 of Test system 1 in the sense that the simulation is not biased. The only difference is that the former requires 9 simulations, while the latter simulates 9 alchemical states serially in just one expanded ensemble simulation. On the other hand, in Simulation 2, we set `HEIGHT` as 0 so that both simulations are not biase and should generat similar results. Compared to the first test system, 

#### Section 2-1. Simulation 1: Vanilla simulations at different $\lambda$ values 
- Path in the repository: `MetaD_EXE_TestSys/System2/Test_1/Vanilla`
- As demonstrated in the [tutorial provided by Alchemistry](http://www.alchemistry.org/wiki/GROMACS_4.6_example:_Direct_ethanol_solvation_free_energy), here we also define 9 intermediate alchemical states. In the section, we will run 9 different simulations (5 ns for each), with the same `.gro` and `.top` files but different `.mdp` files. The `.mdp` files are only different by one line, ` init-lambda-state = X`, where `X` ranges from 0 to 8.
- To begin with, copy the input files in `Prep/Final_inputs` to the working directory (`Test_1`), then copy `Test1/EXE_fixed/sys1_expanded.mdp` of Test syste 1 and adapt it into `sys2.0.mdp` with the following changes made:
  - Set `couple-moltype = LIG`, which is defined in `.top` file
  - Set `couple-intramol = no`
  - Set `init-lambda = 0` for different `.mdp` files
  - Turn off options relevant to expanded ensemble, as shown below:
    ```=1
    ; Seed for Monte Carlo in lambda space
    ; lmc-seed                 = 1000
    ; lmc-gibbsdelta           = -1
    ; lmc-forced-nstart        = 0
    ; symmetrized-transition-matrix = yes
    ; nst-transition-matrix    = 100000
    ; wl-scale                 = 0.8
    ; wl-ratio                 = 0.6 ; keep this low, because the generations are short
    ; init-wl-delta            = 0.5 ; '20' to start, read from the logfile for restarts.       

    ; expanded ensemble variables
    ; nstexpanded              = 10
    ; lmc-stats                = no
    ; lmc-move                 = metropolized-gibbs
    ; lmc-weights-equil        = wl-delta
    ; weight-equil-wl-delta    = 0.0001
    ```
  - Define the alchemical states as follows:
    ```=1
    ; lambda-states          = 1      2      3      4      5      6      7      8      9
    coul-lambdas             = 0.00   0.20   0.50   1.00   1.00   1.00   1.00   1.00   1.00
    vdw-lambdas              = 0.00   0.00   0.00   0.00   0.20   0.40   0.60   0.80   1.00
    ```
- Note that `free-energy` should be turned on (`free-energy = yes`) so that a `.dhdl` file will be generated.
- At this moment, the directory should look like:
  ```
  (base) wei-tse@castlepeak:~/Documents/MetaD_EXE_TestSys/System2/Test_1$ ls
  sys2.gro  sys2_prep_test1.sh  sys2.top  sys2_vanilla.0.mdp
  ```
  Here, we will create a folder (`state_X`) for each alchemical state and run each simulation. To do this, execute `bash sys2_test1_run.sh`, whose content is as follows:
  ```bash=1
  #!/bin/sh

  for (( i=0; i<9; i=i+1 ))
  do
      mkdir state_${i}
      cp *gro *top state_${i}
      cd state_${i}
      cp ../sys2_vanilla.0.mdp sys2_vanilla.${i}.mdp
      sed -i -e "s/init-lambda-state        = 0/init-lambda-state        = ${i}/g" sys2_vanilla.${i}.mdp    
      gmx grompp -f sys2_vanilla.${i}.mdp -c *gro -p *top -o sys2.${i}.tpr
      cd ../
  done

  mkdir Init
  mv *gro *top *mdp Init

  for (( i=0; i<9; i=i+1 ))
  do
      cd state_${i}
      gmx mdrun -deffnm sys2.${i} -dhdl sys2.${i}.dhdl.xvg
      cd ../
  done
  ```
- Specifically, what `sys2_test1_run.sh` does, is to copy the simulation input files (`.gro`, `.mdp`, `.mdp`) to each newly created folder `state_X`, modify the `.mdp` file, generate a `.tpr` and execute `gmx mdrun` to run the simulation for each state.
- As a result, for each alchemical state, it took about an hour to finish a vanilla simulation (with `free-energy = no`) of 5 ns.

#### 2-2. Simulation 2: Stadard alchemical metadynamics (no biases)
- Path in the repository: `/MetaD_EXE_TestSys/System2/Test_1/MetaD_EXE`
- To get started, copy the input files: `cp ../../Prep/Final_inputs/*` in `MetaD_EXE`. (Also copy the `.mdp` file of Test 1: `cp ../Vanilla/state_0/sys2_vanilla.0.mdp sys2.mdp` in `MetaD_EXE`.)
- Modify `sys2.mdp` such that the options relevant to expanded ensemble are turned on, but `lmc-stats` remains `no` so that no biases will be added. Specifically, the part of the `.mdp` file corresponding to Section 2-1 is shown below:
  ```=1
  ; Seed for Monte Carlo in lambda space
  lmc-seed                 = 1000
  lmc-gibbsdelta           = -1
  lmc-forced-nstart        = 0
  symmetrized-transition-matrix = yes
  nst-transition-matrix    = 100000
  ; wl-scale                 = 0.8
  ; wl-ratio                 = 0.6 ; keep this low, because the generations are short
  ; init-wl-delta            = 0.5 ; '20' to start, read from the logfile for restarts.

  ; expanded ensemble variables
  nstexpanded              = 10
  lmc-stats                = no
  lmc-move                 = metropolized-gibbs
  ;lmc-weights-equil        = wl-delta
  ;weight-equil-wl-delta    = 0.0001
  ```
  In addition, change `free_energy` from `yes` to `expanded` such that GROMACS is able to recognize the parameters above. 
- Copy the PLUMED input file from Test 1 (Simulation 2: MetaD_EXE) of Test System 1: `cp ../../../System1/Test_1/MetaD_EXE/plumed.dat .`. Specify both `GRID_MAX` and `GRID_BIN` as 8. (No `GRID_SPACING` is required.) Specifically, the content of the input PLUMED file is as below:
  ```=1
  lambda: EXTRACV NAME=lambda

  METAD ...
  ARG=lambda
  SIGMA=0.01     # small SIGMA ensure that the Gaussian approaximate a delta function
  HEIGHT=0       # In this case, the wegiths in EXE_fixed are fixed, meaning no biasing potentials added        
  PACE=10        # should be nstexpanded
  GRID_MIN=0     # index of alchemical states starts from 0
  GRID_MAX=8     # we have 6 states in total
  # GRID_SPACING=1 # so that the values of CV should be 0, 1, 2, 3, 4, 5
  GRID_BIN=8
  LABEL=metad    # it's not clear how GRID parameters will have influences here
  FILE=HILLS_LAMBDA
  ... METAD

  PRINT STRIDE=10 ARG=lambda,metad.bias FILE=COLVAR
  ```
- Commands
    - `gmx grompp -f sys2.mdp -c sys2.gro -p sys2.top -o sys2.tpr`
    - `gmx mdrun -s sys2.tpr -x sys2.xtc -c sys2_output.gro -e sys2.edr -dhdl sys2_dhdl.xvg -g sys2.log -plumed`
- As a result, it took about 50 minutes to finish the simulation.

#### 2-3. Comparison of the results between the simulations
- Preprocessing of Simulation 1 </br>
To gather `.dhdl` files of each replica, we execute the following bash script (`bash get_dhdl.sh`):
  ```bash=1
  #!/bin/sh
  echo This shell script copy the *dhdl.xvg file from each folder to a newly made folder called dhdl_files and rename all the *dhdl.xvg files.

  set -e     # exit upon error
  read -p "Please input the common prefix of the files: " p
  read -p "Please input the number of replica/intermediate states: " N
  read -p "Please input the number of *dhdl.xvg files in each folder: " n

  mkdir dhdl_files

  echo Copying/renaming the *dhdl.xvg files ...

  for (( i=0; i<$N; i=i+1 ))
  do
      cp state_${i}/*dhdl.xvg dhdl_files/${p}_dhdl_${i}.xvg

      for (( j=2; j<$n+1; j=j+1 ))
      do
          cp state_${i}/*0${j}.xvg dhdl_files/${p}_dhdl_${i}_part${j}.xvg
      done
  done

  echo Complete!
  ```
- Data analysis of Simulation 1:
  - Solvation free energy </br>
For Simulation 1, simply executing `REMD_free_energy` in `dhdl_files`, we can get the result of the solvation energy of the lactic acid:
    ```
    ====== Results ======
    TI: 16.4492006355138 +/- 0.1771749689051801 kT
    BAR: 15.683426266545636 +/- unknown kT
    MBAR: 15.734086413484784 +/- 0.15214548962351204 kT
    ```
    (Note that in our case here, the vanilla simulations are pretty similar Hamiltonian replica exchange except that there was no exchange between alchemical states, so we can simply use `REMD_free_energy` to analyze the data here.) 
  - Overlap matrix </br>
In addition, there is good overlap between adjacent alchemical states, indicating that the intermediate states we defined here should be sufficient to give a reasonable estimate.
- Data analysis of Simulation 2 </br>
As a result, without biases added in the simulation, the system in Simulation 2 was only able to sample the first two states, which means that there is no overlap except for between the first two states. Also, free energy different can not be estimated accurately due to the lack of probability overlap. 
- Additional test: Simulation 3  
  In Test 1, we've also conducted an addition simulation, which is an expanded ensemble simulation with fixed fixed at 0. However, similarly, the system was only able to sample the first two states. In fact, what happend in Simulation 2 and 3 was not surprising, since Test system 2 is more complicated than Test system 1 and biases are therefore needed for sufficient sampling. 
  
  
### 3. Test 2: Comparison between expanded ensemble and standard alchemical metadynamics
As mentioned, in Test 2, Simulation 1 is an expanded ensemble simulation with weights updated by the Wang-Landau algorithm (`wl_scale`= 0.999999), while Simulation 2 is a standard alchemical metadynamics. 

#### 3-1. Simulation 1: Expanded ensemble simulation with updating weights
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
    
#### Section 3-2. Standard alchemical metadynamics
- Path in the repository: `/MetaD_EXE_TestSys/System2/Test_2/MetaD_EXE`
- Here we use the same `.tpr` file as Simulation 1 (hence the same GROMACS parameters). Similarly, we the same PLUMED input file as Simulation 2 in Test 2 except that the `HEIGHT` is specified as 0.5 instead of 0. 
- Commands
    - `gmx grompp -f sys2.mdp -c sys2.gro -p sys2.top -o sys2.tpr`
    - `gmx mdrun -s sys2.tpr -x sys2.xtc -c sys2_output.gro -e sys2.edr -dhdl sys2_dhdl.xvg -g sys2.log -plumed`

#### Section 3-3. Comparison of the results between the simulations
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
  This is an issue that we are currently looking into.



### 4. Test 3: Comparison between expanded ensemble and well-tempered alchemical metadynamics 
In the second test of the lactic system, we want to use expanded ensemble simulation to estimate the solvation free energy. Here, we use exactly the same 9 itermediate states defined in Test 1, but we only have to run one simulation, which requires only one `.gro`, `.top` and `.mdp` file, respectively. In the expanded ensemble, we will start from 0 weights and use Wang-Landau algorithm to update the weights.
- To get started, copy the simulation input files from `Prep/Final_inputs` to the working directory, then copy `Test_2/sys1_expanded.mdp` of Test system 1 and make the following changes:
  - Set `couple-moltype           = LIG`
  - Set `couple-intramol          = no`
  - Define the alchemical states as follows:
  ```
  ; lambda-states          = 1      2      3      4      5      6      7      8      9
  coul-lambdas             = 0.00   0.20   0.50   1.00   1.00   1.00   1.00   1.00   1.00
  vdw-lambdas              = 0.00   0.00   0.00   0.00   0.20   0.40   0.60   0.80   1.00
  ```
- To run the simulation, execute the following commands
  ```
  gmx grompp -f sys2_expanded.mdp -c sys2.gro -p sys2.top -o sys2.tpr 
  gmx mdrun -deffnm sys2 -dhdl sys2.dhdl.xvg
  ```
- As a result, it took about an hour to finish the expanded ensemble (5 ns) and the esitmations of solvation free energy are shown as below:
  ```
  ====== Results ======
  TI: 17.346067712560778 +/- 0.4395560964511634 kT
  BAR: 16.34251431514915 +/- unknown kT
  MBAR: 16.386114373893367 +/- 0.4208061041630484 kT
  ```
  Similarly, with the specified intermediate states, there is good amount of overlap between alchemical states.

## Test system 3: CB8-G3: a host guest binding complex
CB8-G3 binding complex is composed of  cucurbit[8]uril (CB8, host) and quinine (G3, guest) and is one of the host-guest binding complexes in SAMPL6 SAMPLing challenge. Unlike other two host-guest binding complex (OA-G3 and OA-G6) in the same challenge, CB8-G3 is a more challenging case due to the water exclusion problem. In the [SAMPL6 paper](https://link.springer.com/content/pdf/10.1007/s10822-020-00290-5.pdf), it was shown that with expanded ensemble, it was not possible to equilibrate the Wang-Landau weights within the same time as OA-G3/G6. Moreover, OpenMM/SOMD and NAMD/BAR replicate calculations could not converge the average free energy to uncertainties below 1 kcal/mol, and OpenMM/HREX and AMBER/APR displayed a significant and slowly decaying bias. Therefore, here we want to see if alchemical metadynamics is able to outperform the existing methods. To this end, in the first test, we perform a 1-dimensional metadynamics biasing the number of water molecules in the binding cavity. Basically, the file preparation and the metadynamics follow the same protocal as done in the note [Water Exclusion Problem of OA-G3 Host-guest Binding Complex](https://hackmd.io/@WeiTseHsu/water-exclusion).
<img src=https://i.imgur.com/W5Z1DV5.jpg width=350><img src=https://i.imgur.com/KKcWqD9.jpg width=345>

### 1. Preparation of the input files
- The simulation input files (`.gro` and `.top` files) of 5 different configurations of the host-guest binding complex (from `CB8-G3-0` to `CB8-G3-4`) can be found in [SAMPL6](https://github.com/samplchallenges/SAMPL6.git) repository, or specifically, in the directory`SAMPL6/host_guest/SAMPLing`.(For more information, please see [SAMPLing Challenge Instructions](https://github.com/samplchallenges/SAMPL6/blob/master/SAMPLing_instructions.md) or the [SAMPL6 paper](https://link.springer.com/content/pdf/10.1007/s10822-020-00290-5.pdf).)
- To start with, in the folder `Prep`, we copy the files in `CB8-G3-0/GROMACS` in the original repository to the folder `files_from_SAMPLing`. Then, we create anoter folder `MD` in `Prep`, performing a vanilla MD simulation in an NPT ensemble using the same `.mdp` file used in the inputs preparation in the note [Water Exclusion Problem of OA-G3 Host-guest Binding Complex](https://hackmd.io/@WeiTseHsu/water-exclusion).
- As a result, it took about 1.5 hour to finish a MD simulation of 5 ns. To conduct our tests in an NVT ensemble, we need to extract the configuration at the time frame that has the volume that is closet to the average value.
    - To do so, first execute:
      ```
      gmx energy -f md.edr -o volume.xvg
      ```
    - As a result, the STDOUT like below should show:
      ```
      Data analysis of the file: volume.xvg
      =====================================
      Analyzing the file ...
      Plotting and saving figure ...
      The average of volume: 66.866 nm^{3}  (RMSF: 0.006 nm^{3}  max: 68.127 nm^{3} , min: 64.356 nm^{3} )
      The maximum occurs at 0.3200 ns, while the minimum occurs at 0.0020 ns.
      The configuration at 1.564 ns has the volume (66.866394 nm^{3} ) that is cloest to the average volume.
      ```
    - To extract the configuration from the trajectory, execute (select `0` in the prompt):
      ```
      gmx trjconv -s complex_md.tpr -f traj_comp.xtc -o complex_nvt.gro -dump 898
      ```
    - Lastly, to gather the input files for our tests here, in the folder `Final_inputs/NVT`, we execute:
      ```
      cp ../../MD/complex_nvt.gro sys3.gro
      cp ../../files_from_SAMPLing/complex.top sys3.top
      ```
      Similarly, to gather the input files for simulations in an NPT ensemble, in `Final_input/NPT`, execute:
      ```
      cp ../../MD/complex_md.gro sys3.gro
      cp ../../files_from_SAMPLing/complex.top sys3.top
      ```
- More about the system of interest
    - Note that the indices in `.gro` file and PLUMED all start from 1, while the indices in VMD start from 0.
    - There are 1 host molecule, 1 guest molecule, 6 sodium ions, 7 chloride ions and 2150 water molecules in the system.
    - Host molecule: atom 1 to atom 144 (in VMD: `index 0 to 143`)
    - Guest molecule: atom 145 to atom 193 (in VMD: `index 144 to 192`)

### 2. Test 1: Standard 1D metadynamics
- As mentioned, in Test 1, we use the number of water molecules in the binding cavity, which is computed by counting the water molecules with at least one atom within the convex hull of the heavy atoms of CB8. 
    
    
## Appendix: Installation of PLUMED and GROMACS
```terminal=1
git clone --single-branch --branch lambda-metadynamics https://github.com/ptmerz/plumed2.git
mkdir plumed2_build
cd plumed2
./configure --prefix=/home/wei-tse/Documents/Software/PLUMED/plumed2_build CXX=g++ CC=gcc
make -j 4
make install 
(Download the source code of GROMACS 2020.1 from ftp://ftp.gromacs.org/pub/gromacs/gromacs-2020.1.tar.gz and enter the directory where the source code is saved.)
wget ftp://ftp.gromacs.org/pub/gromacs/gromacs-2020.2.tar.gz

tar xfz gromacs-2020.2.tar.gz 
cd gromacs-2020.2 
mkdir build 
cd build 
rm -rf * 
cmake .. -DREGRESSIONTEST_DOWNLOAD=ON -DCMAKE_CXX_COMPILER=g++-7 -DCMAKE_C_COMPILER=gcc-7 -DCMAKE_PREFIX_PATH="/usr/lib/x86_64-linux-gnu;/lib/x86_64-linux-gnu"
make
make check
cd ../gromacs-2020.2/
plumed patch -p 
cd build
sudo make install
source /usr/local/gromacs/bin/GMXRC









tar xfz gromacs-2020.1.tar.gz
cd gromacs-2020.1/
plumed patch -p
mkdir build
cd build
cmake .. -DGMX_BUILD_OWN_FFTW=ON -DREGRESSIONTEST_DOWNLOAD=ON
make
make check
sudo make install
source /usr/local/gromacs/bin/GMXRC

```