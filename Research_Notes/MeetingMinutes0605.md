# Minutes of the meeting on 06.05.2020
###### tags: `MetaD-EXE-TestSys`
*This note is based on the first implementation of MetaD-EXE (related research notes: version 1.x of [Test systems for the development of MetaD-EXE sampling method](/Op4zoHsKSQebhY5xrQmadw)), which can be found in [this commit](https://github.com/ptmerz/plumed2/commit/594ab6d2cf7f16928063e00381d87f633f95ca7a) in branch `lambda-metadynamics` in Pascal's fork of `plumed2`.*

## 1. Summary of the testing results
| -                                | Test 1                                    | Test 2                                           |
| -------------------------------- | ----------------------------------------- | ------------------------------------------------ |
| Type of EXE in Simulation 1      | Weights fixed at 0 (no biasing potential) | Weights updated by the WL algorithm              |
| Type of Meta-EXE in Simulation 2 | standard                                  | standard                                         |
| Parameters                       | `HEIGHT = 0`                              | `HEIGHT` = `init-wl-delta`, `wl-scale` =0.999999 |
- Test 1 (including Simulation 1 and Simulation 2) and Test 2 (including Simulation 1 and Siulation 2) in Test system 1 have been completed. All the simulation details are documented in [Test systems for the development of MetaD-EXE sampling method](/Op4zoHsKSQebhY5xrQmadw). Simulation files have been pushed to [the project repository](https://github.com/wehs7661/MetaD_EXE_TestSys/commit/443f88889b6deb97394270bca866b4dbcd52a464).
- Test 1 in Test system 1
    - According to the comparison of the final histogram and the state visited as a function of time, Simulation 1 and Simulation 2 exhibit similar sampling behaviors.
    - Difference between free energy difference calculated from Simulation 1 and Simulation 2 is about 0.3 to 0.7 kT but the results are statistically consistent according the the uncertainy of the free energy differences estimated by different methods.
- Test 2 in Test system 1
    - Simulation 2 of Test 2 failed due to the following error:
      ```
      Fatal error:
      Something wrong in choosing new lambda state with a Gibbs move -- probably
      underflow in weight determination.
      Denominator is:   0 1.0000000000e+00
      i                dE        numerator          weights
      0 -4.3389062500e+02 0.0000000000e+00-7.9695000000e+03
      1 -1.0062548828e+02 1.9618178501e-44-7.9690000000e+03
      2 -5.1916992188e+01 2.8361995012e-23-7.9685000000e+03
      3 -3.8954101562e+01 1.2090621908e-17-7.9695000000e+03
      4 -3.6776855469e+01 1.0666319960e-16-7.9720000000e+03
      5  0.0000000000e+00 1.0000000000e+00-7.9370000000e+03
      ```
      As shown in the `.log` file, the weight of the first state was not shifted to 0. (Note that we didn't see this issue in Test 1 because that the weights were not adjusted at all in the simulation.) This might be related to this error. Pascal will look into this in the near future.
- For more details about the result, please refer to [Test systems for the development of MetaD-EXE sampling method](/Op4zoHsKSQebhY5xrQmadw).

## 2. Summary of the issues found
- High computational cost of alchemical metadynamics
  In Simulation 2 of Test 1 and Test 2 (both are alchemical metadynamics simulations), it was found that the computational cost was very high such that it took about 8 hours to complete a simulation while it only took about 15 minutes to complet Simulation 1 in both tests. (*06.09. Update: The problem can be solved by specifying `GRID_*` parameters.*)
- The values of collective variable
In the PLUMED output files of Simulation 1 in Test 1 (Test system 1), including `COLVAR` and `HILLS_LAMBDA`, the values of the variable `lambda` range from 0 to 5 rather than 0 to 1. The values in `COLVAR` are all integers (from 0 to 5), showing that the values recorded were not actually the values of the alchemical variable ($\lambda_{vdW}$), but the indices of the alchemical states. (Since we have 6 states, the indices range from 0 to 5.) Same thing happens in Simulation 2 in Test 2 and the free energy difference between the coupled and the uncoupled state seems wrong (it was a vary large difference). It might be worthy to check if PLUMED biased correctly, since the collective variable should be the alchemical variable $\lambda_{vdW}$, rather than the index of the states.
- Underflow error in Simulation 2 in Test 2
  See the result of Simulation 2 of Test 2 in the previous section.

## 4. Questions
- The current implementation of alchemical metadynamics requires the expanded ensemble parameters in the .mdp file to be turned on. However, if the results we get from alchemical metadynamics are similar to those obtained in expanded ensemble, how can we tell if the results from metadynamics were not dominated by the expanded ensemble parameters in the .mdp file? Specifically, what’s the difference between the work done by the EXE parameters in .mdp and the work done by the parameters defined in PLUMED input file in alchemical metadynamics?
- We know that the alchemical metadynamics can be equivalent to expanded ensemble in the sense that the Gaussian biasing potentials are almost as narrow as a delta function in the alchemical direction. Not considering the random factor in the simulation (could simply fixing the random seed work?), will the alchemical metadynamics produces exactly the same results as the expanded ensemble?
- In Test system 1, we only scaled the van der Waals interactions, so there is only one alchemical variable. In the future, we will need to scale different kinds of intermolecular interactions and restraints at the same time. In this case, do we need multi-dimensional alchemical variables (each of them ranges from 0 to 1) or just one-dimensional alchemical variable concatenating all the components in the alchemical vector (like 0, 0.1, 0.2, …. , 0.9, 1.0, 0.0, 0.2, 0.4, …., 0.8, 1.0, 0.0, 0.1, 0.2, …, 0.9, 1.0). What is the difference (advantages/disadvantages) between these two methods? It might be easier to get the free energy difference between the coupled state and the uncoupled state if the one-dimensional alchemical variable is used, but would it be harder to apply biases? Or, would it be reasonable that we use the state number/index as the collective variable instead?
- Another potential issue that I found here is that the value of `init-wl-delta` might influence the accuracy of the result of free energy difference when the standard alchemical metadynamics. As shown above, the smallest units for the weights is 0.5, which might lead to an inaccurate estimation of free energy by MBAR. (This is somehow just my instinct though, I need to think more about this.) Typically, when running an expanded ensemble simulation, we start with `init-wl-delta = 0.5` so that it is not too difficult for the system to generate a flat histogram at the beginning. Since the Wang-Landau incrementor will be updated, it is fine to start with a "large" (aroud 0.5 to 1) Wang-Landau incrementor. (We never use a large `wl-scale` like 0.999999, we typically use 0.6 to 0.8.) However, if the Wang-Landau incrementor has to be fixed to resemble the standard alchemical metadynamics, then the weights are not very precise (as shown above). Altough we generally also start with `HEIGHT` of the same oder in standard metadynamics, the Gaussian biasing potential spreads out and influence the bias for multiple states in one addition. In our case, the Gaussians are more like spikes and barely influence the neighboring states, so `HEIGHT` as 0.5 will directly influence the precision of the free energy profile. (We compute the free energy profile/free energy difference from metadynamics only from adding up all the Gaussians, which is the negative image of the free energy profile.) I don't have a good sense about solving this issue now. I also need to think more about this.
- Scope of the testing/development
  - Standard alchemical metadynamics
  - Well-tempered alchemical metadynamics
  - Multiple walkers alchemical metadynamics?
  - Lambda dynamics?

## 5. Additional notes
In the current implementation, which only works for the case of standard alchemical metadynamics, we have to specify parameters for alchemical calculations in the PLUMED input file and turn on the parameters related to expanded ensemble at the same time. While this way of specifying parameters works for the standard alchemical metadynamics, it might be hard for the case of well-tempered metadynamics. Based on the following reasons, I think it might be better to only specify all the parameters for alchemical metadynamics in the PLUMED input file instead of both in the PLUMED input file and the GROMACS `.mdp` file. (This means that we should turn off the parameters related to expanded ensemble (or at least turn of the ones related to the Wang-Landau algorithm) in the GROMACS `.mdp` file.)
- As mentioned above, there is no deterministic equation relating `wl-scale` in GROMACS and `BIASFACTOR` in PLUMED. It might not be feasible to specify `wl-scale` if we want to run well-tempered alchemical metadynamics.
- Through the tests that I have conducted, I found the introduction of alchemical metadynamics was extremely expensive. The expanded ensemble simulation for test 1 in the first test sytem (only about 600 atoms) takes less than 20 minutes. However, with `-plumed` flag and the same `.tpr` file, it took 6 to 8 hours to complete the same length of alchemical metadynamics (5 ns). There might be some other reasons involved, but it might be worthy to check if some calculates were repeptitive as we specify parameters both in PLUMED and GROMACS.
- In the current implementation, the way of specifying parameters might make the examination of the functionalities of MetaD-EXE harder. Specifically, if the results we get from alchemical metadynamics are similar to those obtained in expanded ensemble, it is hard to tell  if the reasonable outcome is actually a result of turning on expande ensemble options (like if the results from metadynamics were not dominated by the expanded ensemble parameters in the .mdp file). 
    - **Question**: What is the difference between  the work done by the EXE parameters in .mdp and the work done by the parameters defined in PLUMED input file in alchemical metadynamics?
    - Part of the answer to the question above have been addressed in the bullet point related to `PACE`. But yes, we still need to think about how we can make sure that the outputs of alchemical metadynamics are all resulted from the parameters specified in PLUMED instead of dominated by the ones in the GROMACS `.mdp` file.
    - Note that `wl-scale` is ignored if PLUMED metadynamics is used.  
    - The only parameter that currently needs to match is nstexpanded and PACE which have a trivial dependency. We also require expanded ensemble to be turned on. Finally, we use the lmc-mc-move method defined in the mdp to attempt the lambda moves. All Wang-Landau related parameters are ignored. We should certainly think about a more elegant solution to how we turn things on or off, but there shouldn't be the need complicated parameter equivalence. (Weights update is done by metadynamics, MC moves by GROMACS. We just need to make sure they agree on the stride. )

## 6. Todos 
The following are the action items in order that we need to resolve:
- Decide whether to use lambda value or state (integer) as collective variable (see details in follow-up message)
- Get GRID working (which depends on what we decide for 1.), such that testing is more efficient (such that we need minutes and not hours to get results and understand what goes wrong)
- Pascal needs to understand why we observe a “underflow in weight determination” it test case 2. This only comes up after a certain simulation time, so having 2. solved will make this way easier to investigate
