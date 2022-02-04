import copy 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc 

if __name__ == '__main__':
    # Plot the figures!
    rc('font', **{
       'family': 'sans-serif',
       'sans-serif': ['DejaVu Sans'],
       'size': 10
    })
    # Set the font used for MathJax - more on this later
    rc('mathtext', **{'default': 'regular'})
    plt.rc('font', family='serif')

    plt.figure()
    for i in range(2, 10):
        infile = open(f'rep_{i + 1}/plumed.dat', 'r')
        lines = infile.readlines()
        infile.close()

        for line in lines:
            if 'BIASFACTOR' in line:
                gamma = int(line.split('=')[1])
                break

        data = np.transpose(np.loadtxt(f'rep_{i + 1}/COLVAR'))
        time = data[0]
        dihedral = data[1] * 180 / np.pi
        
        l_t = len(time)
        l_d = len(dihedral)
        time_original = copy.deepcopy(time)
        dihedral_original = copy.deepcopy(dihedral)
        t, N_ratio = [], []
        
        for j in np.arange(15, 105, 5):
            time = time_original[:int(0.01 * j * l_t)]
            dihedral = dihedral_original[:int(0.01 * j * l_d)]
            hist = np.histogram(dihedral, bins=200)[0]
            hist = hist[hist != 0]
            t.append(time[-1])
            N_ratio.append(np.max(hist) / np.min(hist))
        plt.plot(t, N_ratio, label=f'$ \gamma $ = {gamma}')
    
    plt.ylim([0, 12])
    plt.hlines(1, 750, 5000, linestyle='--')
    plt.xlabel('Time (ps)')
    plt.ylabel('Count(max) / Count(min)')
    plt.grid()
    plt.legend()
    plt.savefig('N_ratio.png', dpi=600)

