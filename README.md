MetaD_EXE_TestSys
==============================

## Description
This is a repository for hosting the simulation files of the test systems for the development of MetaD-EXE sampling method. Important directories include:
- `Tutorials`: a quick tutorial about using PLUMED to post-process a trajectory and to perform different variants of metadynamics, including standard metadynamics, well-tempered metadynamics, multi-dimensional metadynamics and multiple walkers metadynamics.
- `System1`: A directory for Test system 1, which is an argon atom in a water box.
  - `System1/Prep`: A directory for the preparation of the simulation input files for each test (`System1/Test_1` and `System1/Test_2`).
  - `System1/Test_1`: A directory for the simulation output files and data analysis of Test 1, which is an expanded ensemble simulation of test system 1 with weights fixed at 0.
  - `System1/Test_2`: A directory for the simulation output files and data analysis of Test 2, which is an expanded ensemble simulation of test system 2 with weights constantly updated by Wang-Landau algorithm.
- `System2`: A directory for Test system 2, which is a lactic acid in a water box.
  - `System2/Prep`: A directory for the preparation of the simulation input files for each test (`System2/Test_1` and `System2/Test_2`).
  - `System2/Test_1`: A directory for the simulation output files and data analysis of Test 1, which is vanilla simulations at fixed lambda states in an attempt to calculate the solvation free energy of the lactic acid.
  - `System2/Test_2`: A directory for the simulation output files and data analysis of Test 2, which is expanded ensemble simulation with weights constantly updated by Wang-Landau algorithm in an attempt to calculate the solvation free energy of the lactic acid.

For more details about the file preparations and the simulations, please refer to the [research note hosted on HackMD](https://hackmd.io/@WeiTseHsu/Byw_6bEBI).
