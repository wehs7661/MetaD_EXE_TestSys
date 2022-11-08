import plumed 
import matplotlib.pyplot as plt

data = plumed.read_as_pandas('COLVAR')
coupled = data[data['lambda']==0]
decoupled = data[data['lambda']==39]

plt.figure()
plt.hist(coupled['d'], bins=200)
plt.xlabel('COM distance (nm)')
plt.ylabel('Count')
plt.title('Fully coupled state ($ \lambda =0$)')
plt.grid()
plt.savefig('coupled_dist_hist.png', dpi=600)

plt.figure()
plt.hist(decoupled['d'], bins=200)
plt.xlabel('COM distance (nm)')
plt.ylabel('Count')
plt.title('Fully decoupled state ($ \lambda =1$)')
plt.grid()
plt.savefig('decoupled_dist_hist.png', dpi=600)

