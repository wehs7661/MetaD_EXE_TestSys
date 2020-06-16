# Test 1: Comparison between vanilla simulations and alchemical metadynamics

###### tags: `MetaD-EXE-TestSys` `TestSystem2`
As mentioned above, Test 1 is more like a sanity check as Test 1 of Test system 1. In Test 1 here, we run a series of vanilla MD simulations at different $\lambda$ values in Simulation 1. This simulation is analogous to Simulation 1 in Test 1 of Test system 1 in the sense that the simulation is not biased. The only difference is that the former requires 9 simulations, while the latter simulates 9 alchemical states serially in just one expanded ensemble simulation. On the other hand, in Simulation 2, we set `HEIGHT` as 0 so that both simulations are not biased and should generate similar results. Compared to the first test system, 

## 1. Simulation 1: Vanilla simulations at different $\lambda$ values 
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

## 2. Simulation 2: Stadard alchemical metadynamics (no biases)
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

## 3. Comparison of the results between the simulations
- Preprocessing of Simulation 1
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
  - Solvation free energy
  For Simulation 1, simply executing `REMD_free_energy` in `dhdl_files`, we can get the result of the solvation energy of the lactic acid:
    ```
    ====== Results ======
    TI: 16.4492006355138 +/- 0.1771749689051801 kT
    BAR: 15.683426266545636 +/- unknown kT
    MBAR: 15.734086413484784 +/- 0.15214548962351204 kT
    ```
    (Note that in our case here, the vanilla simulations are pretty similar Hamiltonian replica exchange except that there was no exchange between alchemical states, so we can simply use `REMD_free_energy` to analyze the data here.) 
  - Overlap matrix 
    In addition, there is a good overlap between adjacent alchemical states, indicating that the intermediate states we defined here should be sufficient to give a reasonable estimate.
- Data analysis of Simulation 2
  As a result, without biases added in the simulation, the system in Simulation 2 was only able to sample the first two states, which means that there is no overlap except for between the first two states. Also, free energy differences can not be estimated accurately due to the lack of probability overlap. 
- Additional test: Simulation 3  
  In Test 1, we've also conducted an additional simulation, which is an expanded ensemble simulation with weights fixed at 0. However, similarly, the system was only able to sample the first two states. In fact, what happened in Simulation 2 and 3 was not surprising, since Test system 2 is more complicated than Test system 1 and biases are therefore needed for sufficient sampling. 
  