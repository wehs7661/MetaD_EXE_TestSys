import numpy as np 
import matplotlib.pyplot as plt 
from matplotlib import rc 

def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    running_avg = (cumsum[N:] - cumsum[:-N]) / float(N)

    return running_avg


if __name__ == "__main__":
    rc("font", **{"family": "sans-serif", "sans-serif": ["DejaVu Sans"], "size": 10})
    # Set the font used for MathJax - more on this later
    rc("mathtext", **{"default": "regular"})
    plt.rc("font", family="serif")

    data = np.transpose(np.loadtxt('bond_length.dat', comments=['@', '#']))

    plt.figure(figsize=(12, 6))
    for i in range(3):
        plt.subplot(2, 3, i + 1)
        plt.plot(data[0] * 2 / 1000, data[i + 1])
        plt.xlabel('Time (ns)')
        plt.ylabel(f'Bond length {i + 1}-{i + 2} (nm)')
        plt.grid()

    for i in range(3):
        N = 50
        running_avg = running_mean(data[i + 1][:2000], N)
        plt.subplot(2, 3, i + 4)
        plt.plot(data[0][N - 1:2000] * 2 / 1000, running_avg)
        plt.xlabel('Time (ns)')
        plt.ylabel(f'Running avg. of B.L. {i + 1}-{i + 2} (nm)')
        plt.grid()

    plt.tight_layout()
    plt.savefig('bond_length.png', dpi=600)
