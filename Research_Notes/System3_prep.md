# Preparation of the input files

###### tags: `MetaD-EXE-TestSys` `TestSystem3`
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