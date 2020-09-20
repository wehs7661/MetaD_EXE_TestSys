import plumed 
import numpy as np
import matplotlib.pyplot as plt

fes=[]
for i in range(1001):
    fes.append(plumed.read_as_pandas("fes_" + str(i) + ".dat"))

deltaF=[]
kT=1.0
for i in range(len(fes)):
    deltaF.append(
        kT*np.log(np.sum(np.exp(fes[i].loc[fes[i]['lambda']==8.0]["file.free"]/kT))/np.sum(np.exp(fes[i].loc[fes[i]['lambda']==0.0]["file.free"]/kT))))

plt.figure()
plt.plot(0.02*np.arange(len(fes)),deltaF)
plt.savefig("delta_f.png", dpi=600)
