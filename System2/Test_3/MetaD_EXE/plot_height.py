import plumed
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc

if __name__ == '__main__':
    rc('font', **{
       'family': 'sans-serif',
       'sans-serif': ['DejaVu Sans'],
       'size': 10
       })
    # Set the font used for MathJax - more on this later
    rc('mathtext', **{'default': 'regular'})
    plt.rc('font', family='serif')

    fig = plt.figure(figsize=(12, 10))
    for i in range(20):
        hills = plumed.read_as_pandas(f'rep_{i + 1}/HILLS_LAMBDA')
        t = np.array(hills["time"]) / 1000
        h = np.array(hills["height"] / hills["biasf"] * (hills["biasf"] - 1)) / 2.478956208925815
        plt.subplot(4, 5, i + 1)
        plt.plot(t, h)
        plt.xlabel('Time (ns)', fontsize=8)
        plt.ylabel('Height (kT)', fontsize=8)
        plt.title(f'Rep {i + 1}', fontsize=8)
        plt.grid()
    plt.suptitle('Biasfactor: 50, PACE: 10 steps', weight='bold')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig('Gaussian_heights.png', dpi=600)
