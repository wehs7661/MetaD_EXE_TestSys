# Preparation of the input files
###### tags: `MetaD-EXE-TestSys` `TestSystem1`
To prepare the simulation input files of Test system 1 for all tests, follow the following steps:
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
        ```=1
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
