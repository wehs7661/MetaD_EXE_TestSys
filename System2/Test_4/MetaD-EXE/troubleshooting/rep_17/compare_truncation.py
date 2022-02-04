import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc

def read_uncertainty(txtfile):
    err = []
    f = open(txtfile, 'r')
    lines = f.readlines()
    f.close()

    for l in lines:
        if 'Block size' in l:
            data = l.split(':')[2]
            err.append(float(data.split('+/-')[1].split('kT')[0]))

    return err

if __name__ == '__main__':
    rc('font', **{
       'family': 'sans-serif',
       'sans-serif': ['DejaVu Sans'],
       'size': 10
    })
    rc('mathtext', **{'default': 'regular'})
    plt.rc('font', family='serif')
    
    block_size = np.arange(50, 5050, 50)
    err_1 = read_uncertainty('block_analysis_result_truncate_0.5.txt')
    err_2 = read_uncertainty('block_analysis_result_truncate_0.8.txt')


    plt.figure()
    plt.plot(0.02 * block_size, err_1, label='Truncation fraction = 0.5')
    plt.plot(0.02 * block_size, err_2, label='Truncation fraction = 0.8')
    plt.xlabel('Block size (ps)')
    plt.ylabel('Uncertainty ($ k_{B}T $)')
    plt.title('Uncertainty as a function of block size (Rep 1)')    
    plt.grid()
    plt.legend()
    plt.savefig('compare_truncation.png', png=600)


