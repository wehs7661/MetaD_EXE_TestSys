MetaD_EXE_TestSys
==============================

## Description
This is a repository for hosting the simulation files of the test systems for the development of MetaD-EXE sampling method. Important directories include:
- `sys1`: A directory for Test system 1, which is an argon atom in a water box.
- `sys1/Prep`: A directory for the preparation of the simulation input files for each test (`sys1/Test_1` and `sys1/Test_2` so far).
- `sys1/Test_1`: A directory for the simulation output files and data analysis of Test 1, which is an expanded ensemble simulation of test system 1 with weights fixed at 0.
- `sys1/Test_2`: A directory for the simulation output files and data analysis of Test 2, which is an expanded ensemble simulation of test system 2 with weights constantly updated by Wang-Landau algorithm.

For more details about the file preparations and the simulations, please refer to the [research note hosted on HackMD](https://hackmd.io/@WeiTseHsu/Byw_6bEBI).
