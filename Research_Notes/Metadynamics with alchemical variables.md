# Metadynamics with alchemical variables
###### tags: `MetaD-EXE-TestSys`

Inspired by the theory of expanded ensemble (EXE), we implemented metadynamics (MetaD) with lambda variables, or alchemical metadynamics ($\lambda$-MetaD), which leverages the usage of alchemical intermediate states by performing Monte Carlo (MC) moves in the alchemical space aided by the biasing potentials accumulated through metadynamics. As a progress report, here we summarize the important details of the implementation of the method and the results obtained from the chosen test systems. 

## 1. Implementation
In our implementation of alchemical metadynamics, MC moves in the alchemical space are carried out by the free energy functionalities enabled in GROMACS, while the biasing potentials are applied by PLUMED. To launch an alchemical metadynamics simulation, one can simply utilize an MD parameters (`.mdp`) file valid for expanded ensemble, with additional parameters relevant to the Gaussian biasing potentials specified in PLUMED input file. Note, however, parameters related to the Wang-Landau algorithm, such as `wl-scale`, `wl-ratio`, and `init-wl-delta` are deactivated in alchemical metadynamics. In addition, in alchemical metadynamics, the GROMACS parameter `nstexpanded` is only responsible for the MC jumps between alchemical states, not for adding weights to any states. The weights of alchemical states are only updated by PLUMED. The comparison between the parameters used in expanded ensemble in GROMACS and the ones used in alchemical metadynamics in PLUMED, including the notations, are shown in Table 1. What is noteworthy here is that the Wang-Landau incrementor $\Delta w$ is updated by the Wang-Landau scaling factor (`wl-scale` or $f$) only if the histogram is considered flat, namely, $N_{\text{ratio}} > r$ and $1/N_{\text{ratio}} > r$, where $N_{\text{ratio}}$ is the ratio of the number of samples at each histogram to the average number of samples at each histogram and $r$ is the Wang-Landau ratio. On the other hand, the height of the Gaussian biasing potential is updated periodically in alchemical metadynamics. Therefore, the Wang-Landau scaling factor is not entirely equivalent to the bias factor used in alchemical metadynamics even though they both decrease the biasing weights applied to the alchemical space. 

<center><img src=https://i.imgur.com/8noG8MS.png width=600></center>
<center> Table 1. Parameters used in expanded ensemble and alchemical metadynamics </center>


## 2. Methods 
### 2-1. An overview of the chosen test systems
The ultimate goal of our study is to show that by combining alchemical collective variable (CV) and configurational CV, alchemical metadynamics facilitates the escape of metastable states and the relevant free energy calculations that are not allowed in an expanded ensemble simulation. To this end, in our study, we first tested our implementation of alchemical metadynamics from three different levels, including (1) a sanity check for the features enabled in alchemical metadynamics, (2) a physical validation of 1D and 2D alchemical metadynamics, and (3) a comparison between alchemical metadynamics and expanded ensemble in terms of efficiency. Each of these levels is examined by a model system characteristic of a certain alchemical process as described below.

Specifically, in System 1, we adopted an argon atom in water as our toy model. In the tests of this system, we specified 6 alchemical intermediate states gradually turning off the van der Waals interactions to disappear the argon atom from water. That is, the free energy difference relevant to this alchemical process is the solvation free energy of the argon atom. The simplicity of this system enables comprehensive sampling and easy free energy calculations, which allows us to quickly examine if the extended functionalities of alchemical metadynamics are all correctly implemented. 

After making sure that all features required to run an alchemical metadynamics simulation are reasonably enabled, in System 2, we considered an L-form lactic acid in water. As shown in Figure 1, atom 4 and 11 form an intramolecular hydrogen bond. In the alchemical process where the lactic acid disappears from water. This intramolecular hydrogen bond imposes an energy barrier between metastable states with different torsional angles, making the system kinetically trapped at the uncoupled state ($\lambda=0$), which is equivalent to the lactic acid being in the vacuum. Therefore, the torsional angle relevant to the intramolecular hydrogen bond, which is formed by atom 1, 2, 4, and 5, is the additional configurational CV that could be considered in this system. This additional complexity allows us to test if our implementation of alchemical metadynamics, in either 1D or 2D, is able to overcome an intermediate energy barrier, which is the goal that could be reached by comparing the results of free energy calculations obtained from alchemical metadynamics and the ones from expanded ensemble. 

Lastly, in System 3, we investigated an even more complicated system, which is CB8-G3 host-guest binding complex composed of a cucurbit[8]uril (CB8, host) and a quinine (G3, guest). This host-guest binding complex was one of the systems of interest in the SAMPL6 SAMPLing challenge. It is relatively hard compared to other binding complexes in the same challenge due to the water exclusion problem[^ref1]. That is, the slow motion of water molecules entering and exiting the binding cavity lengthens the timescale of the binding / unbinding event of the guest molecule. Therefore, we considered the number of water molecules near the binding cavity as the configurational CV that could be additionally considered in a 2D alchemical metadynamics. This configurational CV can be estimated by enumerating the number of water molecules in the sphere shown in Figure 2, where the ring molecule is the host molecule, CB8, and the other is the guest molecule. Overall, given that expanded ensemble could hardly solve this problem, we utilized this challenge to show that 
- Alchemical metadynamics could be more robust than expanded ensemble in complicated systems while still providing reasonable free energy estimates
- The introduction of a configurational CV could further facilitate the sampling of complicated systems.

<center>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src=https://i.imgur.com/ytuTsXT.png width=250>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src=https://i.imgur.com/tLvTeP0.png width=420>
</center>
<center> Figure 1. System 2: L-form lactic acid &nbsp; &nbsp;  &nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Figure 2. System 3: CB8-G3 binding complex </center>

### 2-2. Comparison between expanded ensemble and alchemical metadynamics
In light of the similarity between expanded ensemble and alchemical metadynamics in the sense that both methods apply weights to alchemical states to allow roughly equal sampling, we compared the results obtained from the two methods to validate our implementation. 
Specifically, given the three test systems described above, we performed one to three tests for each of them as summarized in Table 2. As shown in Table 2, in each test, we adopted expanded ensemble with differently specified parameters as Group A and alchemical metadynamics with effectively equivalent parameters as Group B. In Group A, the weights of all expanded ensemble simulations were fixed at either zeros or the values equilibrated by the Wang-Landau algorithm. On the other hand, to make the results obtained from Group B comparable to the ones from Group A, in all the tests performed in Group B, the initial magnitude of the Wang-Landau incrementor ($\Delta w$) was the same as the initial height of the Gaussian biasing potential and the frequencies of applying biases were also the same. In addition, in our tests of alchemical metadynamics, the width of the Gaussian biasing potentials was sufficiently small such that the biasing potential approximated a Dirac delta function. Metroplized-Gibbs sampling was used to perform MC moves in the alchemical space for all expanded ensemble and alchemical metadynamics runs. In the following subsections, we describe simulation details about the tests of each model system. All the relevant simulation files are maintained in the [project repository](https://github.com/wehs7661/MetaD_EXE_TestSys.git) on GitHub, while the theory of metadynamics with alchemical variables is documented [here](https://github.com/shirtsgroup/alchemical_metadynamics). 

<center><img src=https://i.imgur.com/tzTk0WI.png></center>
<center> Table 2. Simulation details of the tests for each system </center>

#### 2-2-1. System 1: argon atom
As mentioned above, the purpose of the tests of System 1 is to examine if the features of alchemical metadynamics are all correctly implemented. We divided the examination into three tests, where each of them examined one functionality enabled in our implementation. Specifically,
- Test 1 was to make sure that our implementation of alchemical metadynamics was able to sample the alchemical space with Monte Carlo moves. 
- Then, in Test 2, we wanted to check if our implementation could appropriately deposit weights in the alchemical space. 
- Lastly, in Test 3, the goal was to demonstrate that well-tempered metadynamics was able to provide free energy estimates comparable to the ones obtained from expanded ensemble. 

In System 1, the common starting configuration for all the tests was prepared under the GROMOS 54a7 force field in the SPC water model. We equilibrated the system first in an NVT then in an NPT ensemble, each for 200 ps. After that, we extracted the configuration from an NPT vanilla molecular dynamics (MD) simulation (5 ns) whose volume corresponded to the average volume in the NPT simulation. Subsequently, all the tests were simulated for 5 ns in an NVT ensemble where the temperature was at 298 K and 6 alchemical states were defined to scale the van der Waals interactions. In the following subsections, we describe the simulation details that we used to reach the goal of each test. 

##### Test 1. Comparison between EXE with 0 weights and $\lambda$-MetaD with 0 heights
In Test 1, we compared expanded ensemble without any weights added with alchemical metadynamics without any biasing weights. That is, both simulations are physically equivalent and should act as a series of MD simulations sampling different alchemical states. By showing the equivalence between the two simulations, in terms of the histogram of the alchemical states and free energy calculations, we could ensure that our implementation was able to correctly perform Monte Carlo moves in the alchemical space. 

##### Test 2. Comparison between EXE with 0 Wang-Landau incrementor and a standard $\lambda$-MetaD
Then, in Test 2, instead of zero biases, we applied constant biases that do not decrease with time to make sure that alchemical metadynamics could appropriately deposit weights in the alchemical space. To make Group A comparable to Group B, we set the Wang-Landau ratio as 0.9999999 so that the Wang-Landau incrementor was almost fixed. 

##### Test 3. Comparison between standard EXE and well-tempered $\lambda$-MetaD
As mentioned, the goal of Test 3 is to show that well-tempered alchemical metadynamics is able to provide an estimate of solvation free energy comparable to the one obtained by expanded ensemble. Specifically, the solvation free energy recovered from each method was compared to the benchmark, which was obtained from an expanded ensemble simulation with the weights fixed at the equilibrated values obtained by the Wang-Landau algorithm. The benchmark simulation was extended to 10 ns such that the uncertainty of the solvation free energy was about 0.1 $k_{B}T$. Since the bias factor is not directly equivalent to the Wang-Landau scaling factor, we just set the bias factor as 50, which ensured a moderate decrease in the biasing potentials. 

#### 2-2-2. System 2: lactic acid
As indicated previously, in System 2, in addition to validating our implementation with 1D alchemical metadynamics of a more complicated system, we wanted to see if alchemical metadynamics with an additional coordinate CV was able to provide a reasonable free energy estimate, such that we can use multi-dimensional alchemical metadynamics in a more complicated system (like System 3) in the hope of accelerating the sampling further. Therefore, we have two simulations in Group B of System 2, which are alchemical metadynamics with or without considering the torsional angle relevant to the intramolecular hydrogen bond as the additional configurational CV. These two simulations, along with the expanded ensemble simulation of Group A, were compared with the benchmark simulation, which was an expanded ensemble simulation with fixed and equilibrated weights. The benchmark simulation was extended to 100 ns to ensure sufficiently small uncertainty (0.1 $k_{B}T$). 


In System 2, we used the same procedure as the one used for System 1 to prepare the common starting configuration for all the tests, except that the topology file was prepared by Open Force Field toolkit. All the simulations of this system were simulated in an NVT ensemble with 9 alchemical intermediate states specified to scale the van der Waals and electrostatic interactions. In the 1D alchemical metadynamics, we set the bias factor as 50 and the simulation length as 5 ns, which was the same as the expanded ensemble in Group A. On the other hand, since the 2D alchemical metadynamics was exploring a much larger configurational space, we set the simulation length as 20 ns and the bias factor as 20, which similarly ensured a moderate decrease in the biasing potentials. 

#### 2-2-3. System 3: CB8-G3 host-guest binding complex
Similarly, the goal of System 3, is to show that alchemical metadynamics is able to provide reasonable free energy estimates, with more emphasis on the comparison of the efficiency between alchemical metadynamics considering the configurational CV or not. That is, we similarly adopted an expanded ensemble in Group A and an 1D and 2D well-tempered alchemical metadynamics in Group B, where the additional configurational CV considered was the number of water molecules near the binding cavity of the host molecule. All simulations in Group A and Group B were compared with the benchmark simulation, which is planned to be extended to at least 100 ns. 

With simulation input files provided by [SAMPL6 SAMPLing challenge](https://github.com/samplchallenges/SAMPL6.git), to prepare the starting configuration for all the tests, which are all in NVT ensemble, we performed a vanilla MD simulation for 5 ns in an NPT ensemble and extracted the configuration corresponding to the average volume.  For System 3, 50 alchemical intermediate states were specified to scale van der Waals interactions, electrostatic interactions, and the distance restraint applied between the host molecule and the guest molecule to avoid the guest molecule from drifting away after unbinding. All the simulations are planned to be performed for 20 ns. 

[^ref1]: Rizzi, A., Jensen, T., Slochower, D. R., Aldeghi, M., Gapsys, V., Ntekoumes, D., ... & Cournia, Z. (2020). The SAMPL6 SAMPLing challenge: Assessing the reliability and efficiency of binding free energy calculations. Journal of computer-aided molecular design, 1-33.


### 3. Results and Discussions
#### 3-1. System 1: argon atom
##### 3-1-1. Results of Test 1 of System 1
As described previously, by showing the equivalence of Group A and Group B, the first test was to show that our implementation was able to correctly perform Monte Carlo moves in the alchemical space. As a result, it was shown that the patterns of the final histograms obtained from the two simulations were very similar, as can be seen in Figure 3. Additionally, as shown in Table 3, both simulations were able to provide a reasonable estimate of the binding free energy even if no biasing weights were added. From the results of System 1, we could conclude that our implementation was able to perform Monte Carlo moves correctly in alchemical space.  

<center><img src=https://i.imgur.com/QFW5AN2.png width=400></center>
<center> Figure 3. The final histogram of the simulations in Test 1 of System 1 </center>

##### 3-1-2. Results of Test 2 of System 1
Similar to Test 1, in Test 2, the histogram of the Group A should be the same as the one obtained in Group B. As a result, due to the simplicity of the system, with biasing weights, the final histogram of both simulations were extremely flat, characterizing RMSF values in the final counts of the samples as 0.00096 and 0.000076, respectively. As for the free energy calculations, since both Group A and Group B in Test 2 of System 1 were non-equilibrium processes, MBAR was not applicable to both cases. The free energy differences were off from the benchmark, which was expected since the biasing weight that did not decrease with time limited the uncertainty of the simulations. Overall, from the results of the RMSF values, we ensured that Gaussian biasing potentials were deposited appropriately in the alchemical metadynamics simulation. 

<center>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src=https://i.imgur.com/z4bYbqr.png width=325>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src=https://i.imgur.com/coR7Qw2.png width=325>
</center>
<center> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Table 3. Free energy calculation of System 1 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Figure 3. Free energy difference as a function of time for System 1 (Benchmark) </center>

##### 3-1-3. Results of Test 3 of System 1
Lastly, in Test 3 of System 1, we compared both the standard expanded ensemble and the well-tempered alchemical metadynamics with the benchmark simulation, which is shown to be well-converged in the 10-ns-simulation in the left panel of Figure 3. Note that we did not expect exactly the same behaviors, say, the sampling of the intermediate states as a function of time, from the two simulations, since they are not physically equivalent. However, they should produce comparable results of free energy estimates. Since the system was not in equilibrium in metadynamics in Group B, we could not use MBAR to analyze the derivative of Hamiltonian with respect to lambda to get the solvation free energy. Therefore, to estimate the solvation free energy from a well-tempered alchemical metadynamics, we repeated the process for 20 times. For each repetition, we averaged the free energy difference between the coupled and uncoupled state over the last nanosecond, then we averaged the 20 values to get the final result and its uncertainty. As a result, as shown in Table 3, the solvation free energy estimated by both methods were statistically consistent with the benchmark, which just validated our implementation of well-tempered alchemical metadynamics. 

#### 3-2. System 2: lactic acid
As mentioned previously, the benchmark simulation is an expanded ensemble of 100 ns fixing the weights at the equilibrated values obtained by the Wang-Landau algorithm. As a result, the free energy estimate was well-converged to the uncertainty of only 0.101 $k_{B}T$ given the 100 ns of simulation, as shown in the right panel of Figure 3. With this benchmark, it is shown in Table 4 that Group A and the first simulation of Group B were able to provide reasonable free energy estimates. We are currently working on the 2D alchemical metadynamics simulations in Group B, which will be done in the near future.  

<center>
<img src=https://i.imgur.com/xHW8sBm.png width=325><img src=https://i.imgur.com/T3AC1Xv.png width=325>
</center>
<center> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Table 4. Free energy calculation of System 2 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Figure 4. Free energy difference as a function of time for System 2 (Benchmark) </center>

#### 3-3. System 3: CB8-G3 host-guest binding complex
Similar to System 2, System 3 compares the free energy difference estimated by expanded ensemble with the ones estimated by well-tempered alchemical metadynamics, either in 1D or 2D. Currently, with 50 alchemical intermediate states, no tests have been done. As for the benchmark simulation, we are currently in the phase of equilibrating the lambda weights with the Wang-Landau algorithm. Once this simulation is finished, we will run another expanded ensemble simulation with the weights fixed at the equilibrated values as the benchmark simulation. The benchmark simulation will be extended to at least 100 ns such that the uncertainty is around 0.1 $k_{B}T$.

## 4. Future work of the project
- Finish 20 repetitions of 2D well-tempered alchemical metadynamics of System 2.
- For System 3, the following should be done:
    - Finish the benchmark simulation.
    - Rerun the simulations for Group A (expanded ensemble with fixed weights) and Group B (1D and 2D 𝜆-MetaD).
    - Compare the efficiency of Group A and Group B.
    - Consider introducing one more coordinate CV: the distance between the host molecule and guest molecule.
    - Complete the thermodynamic cycle to calculate the binding free energy.
    - Determine the binding ensemble of the CB8-G3 system.
- In terms of the implementation, the following work could be considered (to be discussed):
    - MBAR in 2D space
    - Combination of lambda dynamics with metadynamics.

