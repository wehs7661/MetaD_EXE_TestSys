import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc

def gaussian(mu, sigma, x):
    coef = 1 / (sigma * np.sqrt(2 * np.pi))
    inside_exp = -((x - mu) ** 2)/(2 * sigma ** 2)
    return coef * np.exp(inside_exp)


if __name__ == '__main__':
    rc('font', **{
       'family': 'sans-serif',
       'sans-serif': ['DejaVu Sans'],
       'size': 10
    })
    rc('mathtext', **{'default': 'regular'})
    plt.rc('font', family='serif')

    block_size = np.arange(50, 2550, 50)
    mu, sigma = [], []  # for Figure 3
    
    
    # Figure 1: free energy difference
    plt.figure()
    plt.hlines(-3.343, 40, 50, label='Benchmark', color='b', linestyle='--')
    plt.hlines(-3.245, 40, 50, label='Method 1', color='g', linestyle='--')
    plt.xlabel('Block size (ps)')
    plt.ylabel('Free energy difference ($ k_{B}T $)')
    plt.title('Free energy difference as a function of block size')    
    plt.grid()
    
    truncate_f = 0.6
    method = ''  # or ''

    for i in range(20):
        delta_f = []
        
        f = open(f'rep_{i + 1}/block_analysis_result_truncate_{truncate_f}{method}.txt', 'r')
        lines = f.readlines()
        f.close()
        
        for l in lines:
            if 'Block size' in l:
                data = l.split(':')[2]
                delta_f.append(float(data.split('+/-')[0]))
        plt.plot(0.02 * block_size, delta_f, label=f'Rep {i + 1}')
        mu.append(delta_f[0])

    plt.ylim([-2, -5.2])
    plt.legend(ncol=4)
    plt.savefig(f'delta_f_20_reps_truncate_{truncate_f}{method}.png', dpi=600)
    
    # Figure 2: Uncertainty
    plt.figure()
    plt.xlabel('Block size (ps)')
    plt.ylabel('Uncertainty ($ k_{B}T $)')
    plt.title('Uncertainty as a function of time')
    plt.grid()

    for i in range(20):
        delta_f_err = []
        f = open(f'rep_{i + 1}/block_analysis_result_truncate_{truncate_f}{method}.txt', 'r')
        lines = f.readlines()
        f.close()

        for l in lines:
            if 'Block size' in l:
                data = l.split(':')[2]
                delta_f_err.append(float(data.split('+/-')[1].split('kT')[0]))
        plt.plot(0.02 * block_size[:50], delta_f_err[:50], label=f'Rep {i + 1}')
        sigma.append(delta_f_err[24])  # block_size = 25 ps
    
    plt.legend(ncol=4)
    plt.savefig(f'delta_f_err_20_reps_truncate_{truncate_f}{method}.png', png=600)

    # Figure 3: Distribution
    x = np.arange(0, -5.01, -0.01)
    plt.figure()
    plt.xlabel('Free energy difference (kT)')
    plt.ylabel('Probability density')
    plt.title('The distribution of free energy difference of 20 repetitions')
    for i in range(20):
        plt.plot(x, gaussian(mu[i], sigma[i], x), label=f'Rep {i + 1}')
        plt.legend(ncol=2)
    plt.savefig(f'delta_f_distribution_20_reps_truncate_{truncate_f}{method}.png', png=600)

    print(np.std(mu))
    print(mu)
    print(np.mean(mu))
    print(sigma)
    print(np.mean(sigma))



