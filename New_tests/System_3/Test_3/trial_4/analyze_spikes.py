import plumed
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc


if __name__ == "__main__":
    # Plot Gaussian height as a function of time with each CV as the parameter
    rc("font", **{"family": "sans-serif", "sans-serif": ["DejaVu Sans"], "size": 10})
    # Set the font used for MathJax - more on this later
    rc("mathtext", **{"default": "regular"})
    plt.rc("font", family="Serif")

    data = plumed.read_as_pandas('HILLS_2')
    sub_data = data[data['time']>103000]
    unphysical_data = sub_data[sub_data['height']>0.2]

    t = unphysical_data['time']
    h = unphysical_data['height']
    n = unphysical_data['n']
    lambda_ = unphysical_data['lambda']

    plt.figure()
    plt.scatter(t/1000, h, s=1)
    plt.xlabel('Time (ns)')
    plt.ylabel('Gaussian height (kJ/mol)')
    plt.grid()
    plt.savefig('unphysical_heights.png', dpi=600)
    
    plt.figure()
    plt.scatter(t/1000, n, s=1)
    plt.xlabel('Time (ns)')
    plt.ylabel('Number of water molecules')
    plt.grid()
    plt.savefig('unphysical_water.png', dpi=600)

    plt.figure()
    plt.scatter(t/1000, lambda_, s=1)
    plt.xlabel('Time (ns)')
    plt.ylabel('Alchemical state')
    plt.grid()
    plt.savefig('unphysical_lambda.png', dpi=600)


