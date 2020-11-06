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

    block_sizes = np.arange(10, 1010, 10)
    
    delta_f_err = []  # free energy difference and its uncertainty
    for i in block_sizes:
        os.system(f'(echo 0; echo 5; echo 6) | python free_energy_uncertainty.py -b {i}')
        data = np.transpose(np.loadtxt(f'fes_bsize_{i}.dat'))
        fes_err = data[-1]
        delta_f_err.append(np.sqrt(fes_err[-1] ** 2 + fes_err[0] ** 2))
    
    print(f'Free energy difference: {data[-2][-1] - data[-2][0]} kT')
    plt.figure()
    plt.plot(block_sizes, delta_f_err)
    plt.xlabel('Block size (ps)')
    plt.ylabel('Uncertainty ($ k_{B}T $)')
    plt.title('Uncertainty as a function of block size')
    plt.grid()
    plt.savefig('uncertainty_block_size.png', dpi=600)

    os.system('rm fes_bsize*')
