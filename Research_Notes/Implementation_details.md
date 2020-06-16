# Implemntation details
###### tags: `MetaD-EXE-TestSys`


### 1. Equivalence between expanded ensemble (EXE) and alchemical metadynamics (MetaD-EXE)
Alchemical metadynamics biases the alchemical variable as a configurational collective variable. In the case that the Gaussian biasing potentials added to the alchemical intermediate states are very narrow (`SIGMA` is almost 0)such that they approximate Dirac delta function, alchemical metadynamics is almost equivalent to expanded ensemble with non-fixed weights. (We will address the differences between the two later.) This characteristic is one of the important benchmarks that we can use to compare MetaD-EXE with EXE to ensure reasonable performance and robustness of MetaD-EXE along the way of developing it. In this specific case that they are equivalent, some of the simulation parameters defined in the PLUMED input file are related to the parameters in the GROMACS `.mdp` file. 
#### 1-1. `PACE` and `nstexpanded`
`PACE` in the PLUMED input file (stride for adding Gaussian biasing potentials) is equivalent to `nstexpanded` in the `.mdp` file in GROMACS (stride for proposing a move between alchemical states). Note that in an expanded ensemble, the weight of a certain state (either the original state or the proposed state) changes whenever a move is proposed (no matter if the move is accepted). If the move is accepted, the proposed state changes, otherwise the weight of the original state changes. However, we should also note that in metadynamics, in effect, the move is proposed every step, while the move is proposed every `nstexpanded` in an expanded ensemble. Therefore, `PACE` and `nstexpanded` are only equivalent to each other in terms of the stride of changing the weights of alchemical states. 
  - **Question**: In alchemical metadynamics, do the moves between different alchemical states based on MD simulations (just like biasing ordinary conformational collective variables) or MC simulations (just like expanded ensemble)? If they are based on MC simulations, what is the frequency of proposing a move? Also, does it make more sense that we treat the alchemical variable as other conformational collective variables such that we decide whether the system should move to a new state according to the "effective force" based on the potential energy difference between the neighboring state? If the moves are based on MD simulations, then what is the effective frequency of proposing the move? (I think it should be 1 step but I want to make sure.)
  - **Answer**: State changes are via MC at frequency `nstexpandd`. PLUMED does only accumulate the weights, the change of states is done identically to expanded ensemble. Changing the alchemical states through MD simulations is actually lambda dynamics. We decided to focus on MC first in an earlier meeting. Specifically, 
    - In the expanded ensemble simulation, `nstexpanded` does two things. One is proposing a new alchemical state, the other is changing the weights of either the current state (move rejected) or the proposed state (move accepted).
    - In the alchemical metadynamics, `nstexpanded` is only used for changing the state. The frequency of adjusting the weights is not `nstexpanded` but `PACE`. This is one of the reasons that we want to specify both parameters in the current implementation. The behavior of `nstexpanded` can be easily modified by an if statement in the patch of PLUMED, which replaces the corresponding part of the code in GROMACS.
    - As shown above, `nstexpanded` and `PACE` are not exactly equivalent, but the results from different simulations (for example, Simulation 1 and Simulation 2 in Test 1 and Test 2 in Test system 1) should be comparable if they are set to the same values. 
    - Therefore, in the past, we use the Wang-Landau algorithm to adjust the weights of alchemical states, while now what we are trying to do is to develop a method that also uses MC simulation to switch states as in expanded ensemble but uses metadynamics to change the weights of the states.
#### 1-2. `HEIGHT` and `init-wl-delta`
`HEIGHT` in the PLUMED input file (the initial height of the Gaussian biasing potentials) is equivalent to `init-wl-delta` (the initial value of the Wang-Landau incrementor) in the GROMACS `.mdp` file. Note, however, this is true only if the initial Wang-Landau weights is a zero vector. Also, note that adding a Gaussian of height $h$ to an alchemical state is equivalent to *substracting* the Wang-Landau weight of that state by $h$ (so the probability of staying at the original place decreases), where $h=h(t)$ is the height of the Gaussian/value of the WL incrementor at time $t$. 
#### 1-3. `SIGMA` in PLUMED
`SIGMA` specifies the width of the Gaussian biasing potential in PLUMED, but there are no parameters analogous to it in expanded ensemble. (Or, expanded ensemble is mostly equivalent to metadynamics if `SIGMA` is 0.) Sine in MetaD-EE, we only want to add the bias to one state without influencing the weights of any other states, in the current implementation of MetaD-EE, we use small `SIGMA` to make sure that the addition of the bias to the neighbor states is negligible. However, one thing we might have to deal with in the future is that the spacing in the value of alchemical variables ($\lambda_{vdw}$, $\lambda_{coul}$ or $\lambda_{restr}$, ...etc.) of different states in different scaling region might be different, depending on the number of states in that certain region. As a result, we might need to make `SIGMA` variable such that it ensures the Gaussians are narrow enough in all regions. Otherwise, we might need another method to add biases in MetaDEXE to circumvent this issue. 
  - **Comment**: There is no need to have $\lambda$-dependent `SIGMA` as long as we want it to be essentially a delta function - we can just choose the `SIGMA` that is small enough for all the scaling regions. If we want to have `SIGMA` becoming larger, such that neighboring states are getting contribution, then a $\lambda$-dependent `SIGMA` could be necessary. 
#### 1-4. `wl-scale` and `BIASFACTOR`
- `wl-scale` in the GROMACS `.mdp` file controls how fast the Wang-Landau decreases once the histogram is considered flat. Therefore, expanded ensemble with `wl-scale=1` can be analogized to standard alchemical metadynamics, in which the height of the Gaussian biasing potential is constant. On the other hand, if `wl-scale` is smaller than 1, the expanded ensemble corresponds to well-tempered alchemical metadynamics.
- In PLUMED/metadynamics, `BIASFACTOR` is used to control the decreasing of the height of the Gaussians and therefore is similar to `wl-scale` in expanded ensemble. Specifically, the height of the Gaussians $W(k\tau)$ as a function of time ($t=k\tau$) and the bias factor $\gamma$ can be expressed as:
$$\gamma = \frac{T + \Delta T}{T},\;W(k\tau)=W_{0} \exp (-\frac{V(\vec{s}(q(k\tau)), k\tau)}{k_{B}\Delta T})$$
Therefore, the exponential term of $W(k\tau)$ can be regarded as the effective scale factor $s_{eff}$ in metadynamics. Practically, we control $\Delta T$ by specifying the value of $\gamma$, so here we express $s_{eff}$ as a function of $\gamma$ instead of $\Delta T$:
$$s_{eff} = \exp (-\frac{V(\vec{s}(q(k\tau)), k\tau)}{k_{B}(\gamma T - T)})$$ where $T$ is the simulation temperature. However, we should note that $s$ and $s_{eff}$ are analogous but not equivalent to each other, since the height of the Gaussians is updated periodically, while the Wang-Landau incrementor is only updated when the histogram is considered flat and is therefore non-periodic. 

### 2. Additional notes of implementation details
#### 2-1. Collective variables in alchemical metadynamics
In alchemical metadynamics, the CV based on different alchemical states could be either the indices of the states or the values of the alchemical variables. For example, if we have 10 states with the first 5 scaling the electrostatic interactions and the rest of them scaling the van der Waals interactions, the values of the first kind of CV should be 0, 1, 2, ..., 9, while the values of the other CV should be something like 0, 0.2, 0.6, 0.8, 1.0, 0.2, 0.4, 0.6, 0.8, 1.0. Which one is better? Here are a few thoughts:
- If we have non-equally spaced lambda values, the use of the integer value is effectively a mapping into a space with equidistant states. This might make decisions about e.g. the width of Gaussians easier.
- If we have two or more lambda values (e.g. for VdW and electrostatics), which we plan only to traverse in a predefined order (first reducing electrostatics, then vdW), we would anyway need some kind of mapping onto a continuous variable. The state integer already does that.
- If we were to move to a lambda dynamics type of setting, being in state space in PLUMED might make it complicated. (Or maybe not even?) We don’t have any plans in this direction for the time being though. 
- With the alchemical variables being the CV, we might have to think about the dimensionality of the alchemical CV if we need to scale multiple interactions. Specifically, we could either make the CV as 1-dimensional such that each value is actually a vector or make the CV have the same dimensionality as the number of interactions to be scaled. It might be easier to get the free energy difference between the coupled state and the uncoupled state if the one-dimensional alchemical variable is used, but would it be harder to apply biases? 

#### 2-2. Minor things to address in the future
Along the way of development, there are some minor things that we didn't address immediately for the sake of convenience. These minor things do not really influence the simulation results or the validity of our test, but we will address these at the end of the development. Here is a summary of these minor changes to be done in the future:
- Consideration of units
PLUMED uses kJ/mol, so the bias is expected to be in kJ/mol when queried in the GROMACS code. The GROMACS code, however, uses units of kT for the weights. We have two options:
    - Silently use the bias as units of kT instead of kJ/mol. This allows us to use the same numerical values in GROMACS input and Plumed input. No problem expected as long as we are only using lambda metadynamics, but if we start to combine with other CVs, things could get ugly. Also, it's not nice to silently convert interpret input to be in different units... Anyway, this is the solution currently implemented thanks to its simplicity.
    - Transform the bias GROMACS receives from Plumed into units of kT. This is clean but less easy for the user: To get equivalence between GROMACS input and Plumed input, the user needs to do that same transformation, and needs to update it if the simulation temperature changes! This should probably be the longterm solution.

- The counts of the states in MetaD-EXE
The following is a part of the `.log` file of some simple test of MetaD-EXE
![](https://i.imgur.com/AiwzUWK.png)
  As shown above, the energy difference between state 1 and 2 is only $1 \cdot \Delta w$ instead of $2 \cdot \Delta w$ (the difference in counts is 2). This seems to be because that the system starts from state 1 and the counts started from $[1,\; 0,\; 0,\; 0,\; 0,\; 0]$, instead of $[0,\; 0,\; 0,\; 0,\; 0,\; 0]$. That is, PLUMED ignores the starting state and only starts adding bias when the state returns to that state. This doesn't happen in standard expanded ensemble, so we need to address this issue in the future. (In the limit of a lot of samples, the difference should be negligible though.)

For more details about the implementation of MetaD-EXE, please refer to [Pascal's note](https://hackmd.io/@ptmerz/rJFNkXwqU).

### 3. Installation/patching of the modified PLUMED
The development of MetaD-EXE is done by Pascal in [his fork of PLUMED repository](https://github.com/ptmerz/plumed2.git) (branch: `lambda-metadynamics`). To perform validity tests using the latest implementation, we have to install the modified PLUMED and patch it with GROMACS 2020.2 by executing the codes below:
```terminal=1
git clone --single-branch --branch lambda-metadynamics https://github.com/ptmerz/plumed2.git
mkdir plumed2_build
cd plumed2
./configure --prefix=/home/wei-tse/Documents/Software/PLUMED/plumed2_build CXX=g++ CC=gcc
make -j 4
make install 
wget ftp://ftp.gromacs.org/pub/gromacs/gromacs-2020.2.tar.gz

tar xfz gromacs-2020.2.tar.gz 
cd gromacs-2020.2 
mkdir build 
cd build 
rm -rf * 
cmake .. -DREGRESSIONTEST_DOWNLOAD=ON -DCMAKE_CXX_COMPILER=g++-7 -DCMAKE_C_COMPILER=gcc-7 -DCMAKE_PREFIX_PATH="/usr/lib/x86_64-linux-gnu;/lib/x86_64-linux-gnu"
make
make check
cd ../gromacs-2020.2/
plumed patch -p 
cd build
sudo make install
source /usr/local/gromacs/bin/GMXRC
```