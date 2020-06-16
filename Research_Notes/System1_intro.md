# Test system 1: An argon atom in a water box
###### tags: `MetaD-EXE-TestSys`
As a system containing only 661 atoms, Test system 1 serves as a simple toy model for us to examine the functionalities of MetaD-EXE in the easiest way. Here, we take the advantages of the equivalence between expanded ensemble and alchemical metadynamics. Specifically, in the first test, we compare the expanded ensemble with weights fixed at 0 with standard alchemical metadynamics. Since the weights are 0 throughout the expanded ensemble simulation, the results should be similar to what we get from the standard metadynamics with `HEIGHT` being 0. Then, in the second test and the third test, we compare expanded ensemble with updating weights with standard MetaD-EXE and well-tempered MetaD-EXE, respectively. The following table summarizes these three systems:



| -                | Test 1             | Test 2                                           | Test 3                             |
| ---------------- | ------------------ | ------------------------------------------------ | ---------------------------------- |
| Type of EXE in Simulation 1      | Weights fixed at 0 (no biasing potential) | Weights updated by the WL algorithm                                 | Weights updated by the WL algorithm                  |
| Type of Meta-EXE in Simulation 2| standard           | standard                                         | well-tempered                      |
| Parameters       | `HEIGHT = 0`       | `HEIGHT` = `init-wl-delta`, </br>`wl-scale` =0.999999 | `HEIGHT` = `init-wl-delta`, `wl-scale` = 0.8, </br>`BIASFACTOR` = some value |

Below we start with the preparation of the simulation input files for all these tests. All the input files can be found in `Prep/Final_inputs`.










