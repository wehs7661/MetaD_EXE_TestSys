import plumed 
import numpy as np
import matplotlib.pyplot as plt 

if __name__ == "__main__":
    data = plumed.read_as_pandas('analysis.dat')
    n_min, n_max = [], []
    for i in range(20):
        sub_data = data[data['lambda']==i]
        n_min.append(np.min(sub_data['n']))
        n_max.append(np.max(sub_data['n']))

    plt.figure()
    plt.plot(range(20), n_min, label='Minimum of N')
    plt.plot(range(20), n_max, label='Maximum of N')
    plt.xlabel('$\lambda$')
    plt.ylabel('Number of water molecules')
    plt.grid()
    plt.legend()

    plt.savefig('water_number.png', dpi=600)

