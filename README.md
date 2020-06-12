MetaD_EXE_TestSys
==============================

## Description
This is a repository for hosting the simulation files of the test systems for the development of MetaD-EXE sampling method. Important directories include:
- `Tutorials`: a quick tutorial about using PLUMED to post-process a trajectory and to perform different variants of metadynamics, including standard metadynamics, well-tempered metadynamics, multi-dimensional metadynamics and multiple walkers metadynamics.
- `Research_Notes`: Notes of simulation details of all tests in different test systems and minutes of meetings. 
- `System1`: A directory for Test system 1, which is an argon atom in a water box.
  - `System1/Prep`: A directory for the preparation of the simulation input files for each test.
  - `System1/Test_1`: Comparison of the results of expanded ensemble simulation of with weights fixed at 0 (`EXE_fixed`) with standard alchemical metadynamics with 0 biases.
  - `System1/Test_2`: Comparison of the results of expanded ensemble simulation with updating weights (`wl-scale=0.999999`) with standard alchemical metadynamics.
  - `System1/Test_3`: Comparison of the results of expanded ensemble simulation with updating weights (`wl-scale=0.8`) with well-tempered alchemical metadynamics.
- `System2`: A directory for Test system 2, which is a lactic acid in a water box.
  - `System2/Prep`: A directory for the preparation of the simulation input files for each test.
  - `System2/Test_1`: Comparison the results of vanilla simulations at fixed lambda states with standard alchemical metadynamics with 0 biases.
  - `System2/Test_2`: Comparison the results of expanded ensemble simulation with updating weights (`wl-scale=0.999999`) with standard alchemical metadynamics.
  - `System2/Test_3`: Comparison of the results of expanded ensemble simulation with updating weights (`wl-scale=0.8`) with well-tempered alchemical metadynamics.
- `System3`: A directory for Test system 3, which is CB8-G3 host-guest binding complex in the water box.
  - `System3/Prep`: A directory for the preparation of the simulation input files for each test (`System3/Test_1`).
  - `System3/Test1`: Comparison of the results of 1-dimensional metadynamics biasing the number of water molecules in the binding cavity with alchemical metadynamics/

For more details about the file preparations and the simulations, please refer to the [research note hosted on HackMD](https://hackmd.io/@WeiTseHsu/Byw_6bEBI).

