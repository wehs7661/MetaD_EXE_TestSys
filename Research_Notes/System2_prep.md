# Preparation of the input files
###### tags: `MetaD-EXE-TestSys` `TestSystem2`
- Initial configuration
  - As shown above, lactic acid has two enantiomers (stereoisomers that are non-superimposable mirror images), which are the L-form and D-form lactic acid. L-form lactic acid is the natural form that can be processed by human bodies, but it doesn't matter which form of lactic acid we use in our case.
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
  - Here we use Open Forcefield and OpenMM to prepare the system topology and use ParmEd to convert the OpenMM topology to  GROMACS files (including `system.gro` file and `system.top` file). The process can be done by simply executing 
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
  - To ensure that the atom types of the water molecules added and the ions to be added (if needed) can be recognized, we have to add the corresponding atom types in the topology file. In our case, since the net charge of the system is 0 and we are not going to include any buffer solution, we only have to add the atom types relevant to the water molecules in the chosen force field.
  - Note that the output topology of Open Forcefield is an all-atom topology, which implies that we can only use an all-atom force field. Accordingly, here we choose AMBER99SB-ILDN force filed. (Note that it should be fine as long as the force field is all-atom.) 
  - An improper force field (like GROMOS54a7, which is a united-atom force field) might lead to bad contacts between atoms (i.e., the distance between atoms is too small), which results in large forces and numerical instability. When this is the case, one can often observe that in STDOUT of energy minimization, the maximum force is unreasonably large. And a `mdrun` command used for equilibrations will return an error like `step XXX: One or more water molecules can not be settled.`.
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
   - From the topology file `system.top`, we can see that the net charge of the system is 0. In addition, we are not going to include any buffer solution in our case, so we don't need to add additional sodium or chloride ions to the system and can directly proceed with the system to energy minimization.
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