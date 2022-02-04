import os 
import glob
import natsort 
import numpy as np 
import matplotlib.pyplot as plt 
from prettytable import PrettyTable
from matplotlib import rc 

def get_free_energy_diff(fes_file):
    fes = np.transpose(np.loadtxt(fes_file))[-2]
    f_err = np.transpose(np.loadtxt(fes_file))[-1]
    
    delta_f = fes[-1] - fes[0]
    delta_f_err = np.sqrt(f_err[-1] ** 2 + f_err[0] ** 2)

    return delta_f, delta_f_err

def plot_gaussian(mu, sigma, label):
    coef = 1/(sigma * np.sqrt(2 * np.pi))
    x = np.arange(mu - 5 * sigma, mu + 5 * sigma, 0.01)
    y = coef * np.exp(-0.5 * ((x - mu) / sigma) ** 2)
    plt.plot(x, y, label=label)


if __name__ == '__main__':
    # Plotting the results if needed
    rc('font', **{
       'family': 'sans-serif',
       'sans-serif': ['DejaVu Sans'],
       'size': 10
    })
    # Set the font used for MathJax - more on this later
    rc('mathtext', **{'default': 'regular'})
    plt.rc('font', family='serif')
    
    plt.figure()
    for i in range(20):
        files = []
        for f in os.listdir(f'rep_{i + 1}/FES/'):
            if f.endswith('.dat'):
                files.append(f)
        files = natsort.natsorted(files, reverse=False)

        blocks, err = [], []
        for j in files:
            blocks.append(int(float(j.split('_')[2].split('.dat')[0])))
            err.append(get_free_energy_diff(f'rep_{i+1}/FES/{j}')[1])
        
        blocks = np.array(blocks)
        err = np.array(err)
        
        plt.plot(blocks * 0.02, err, label=f'Rep {i + 1}')

    plt.xlabel('Block size (ps)')
    plt.ylabel('Uncertainty ($k_{B}T$)')
    plt.title('Uncertainty as a function of block size')
    plt.ylim([0.03, 0.08])
    plt.grid()
    plt.legend(ncol=4)
    plt.savefig('err_block_20reps.png', dpi=600)

    plt.figure()
    f_list = []
    for i in range(20):
        try:
            delta_f, delta_f_err = get_free_energy_diff(f'rep_{i+1}/FES/fes_bsize_1000.dat')
        except:
            delta_f, delta_f_err = get_free_energy_diff(f'rep_{i+1}/FES/fes_bsize_1000.0.dat')
        f_list.append(delta_f)
        plot_gaussian(delta_f, delta_f_err, f'Rep {i}')
    print(np.mean(f_list))
    print(np.std(f_list))
    
    plt.xlabel('Free energy difference ($k_{B}T$)')
    plt.ylabel('Probability density')
    plt.title('The PDFs of the free energy differences (block size: 20 ps)')
    plt.xlim([-4.27, -0.5])
    plt.grid()
    plt.legend(ncol=2)
    plt.savefig('free_energy_distribution_20reps.png', dpi=600)

    x = PrettyTable()
    x.field_names = []


