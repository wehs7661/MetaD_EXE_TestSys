import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc

if __name__ == '__main__':
    rc('font', **{
       'family': 'sans-serif',
       'sans-serif': ['DejaVu Sans'],
       'size': 10
    })
    rc('mathtext', **{'default': 'regular'})
    plt.rc('font', family='serif')

    block_sizes = np.arange(310, 610, 10)
    
    delta_f, delta_f_err = [], []  # free energy difference and its uncertainty
    for i in block_sizes:
        os.system(f'python free_energy_uncertainty.py -b {i} -g 0 8 9 -t 0.8')
        data = np.transpose(np.loadtxt(f'fes_bsize_{i}.dat'))
        fes_err = data[-1]
        delta_f.append(data[-2][-1] - data[-2][0])
        delta_f_err.append(np.sqrt(fes_err[-1] ** 2 + fes_err[0] ** 2))
        print(f'Block size: {i} ({2 * i} ps), Free energy difference: {delta_f[-1]: .5f} +/- {delta_f_err[-1]: .5f} kT')

    # free energy difference as a function of block size
    plt.figure()
    plt.plot(2 * block_sizes, delta_f)
    plt.xlabel('Block size (ps)')
    plt.ylabel('Free energy difference ($ k_{B}T $)')
    plt.title('Free energy difference as a function of block size')
    plt.grid()
    plt.savefig('delta_f_block_size.png', dpi=600)
    
    # uncertainty as a function of block size
    plt.figure()
    plt.plot(2 * block_sizes, delta_f_err)
    plt.xlabel('Block size (ps)')
    plt.ylabel('Uncertainty ($ k_{B}T $)')
    plt.title('Uncertainty as a function of block size')
    plt.grid()
    plt.savefig('uncertainty_block_size.png', dpi=600)
