# Test system 2: a lactic acid in the water box
###### tags: `MetaD-EXE-TestSys`
In the second test system, we want to compare the alchemical metadynamics with the existing methods for the calculation of the solvation free energy. The system of interest is a lactic acid in the water box, which has only one potential intramolecular hydrogen bond (between the hydrogen atom of the hydroxyl group and the oxygen atom of the carboxyl group). 

To calculate the solvation free energy with currently existing methods, we can either run a bunch of vanilla simulations at different values of the alchemical variable $\lambda$ or run an expanded ensemble simulation. In the tests here, we will specify `couple-intramol = no` to maintain the intramolecular hydrogen bond, which will make the system kinetically trapped at $\lambda=0$, the uncoupled alchemical state which is equivalent to the case of the lactic acid being in the vacuum. Specifically, in a water box (at $\lambda=1$), the lactic acid can form hydrogen bonds either internally or with the water molecules around, which leads to a lower energy barrier along the CV defined as the torsional angle. On the other hand, in vacuum ($\lambda=0$), only one intramolecular hydrogen bond can be formed, so the torsion remains trapped in a certain value. As will be shown below, expanded ensemble is sufficient to overcome the energy barrier, and the goal here is to examine whether the introduction of metadynamics (hence alchemical metadynamics) can accelerate the process further.

<center>
<img src=https://i.imgur.com/WMOFDIg.png width=250><img src=https://i.imgur.com/IQmy1bn.png width=250>
</center>

Specifically, regarding this test system, the following tests will be performed (Note that Simulation 1 is the control group):


| -            | Test 1                                              | Test 2                                                       |
| ------------ | --------------------------------------------------- | ------------------------------------------------------------ |
| Simulaion 1  | Vanilla MD simulations at </br> different $\lambda$ values | Expanded ensemble with </br> updating weights                      |
| Simulation 2 | Standard alchemical metadynamics                    | Well-tempered </br> alchemical metadynamics                                   |
| Parameters   | `HEIGHT=0`                                          | `HEIGHT` = `init-wl-delta`</br>, `wl-scale` = 0.8, `BIASFACTOR`=? |






  




