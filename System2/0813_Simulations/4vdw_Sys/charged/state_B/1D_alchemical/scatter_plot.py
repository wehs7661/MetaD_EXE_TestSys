import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc


if __name__ == "__main__":
    rc("font", **{"family": "sans-serif", "sans-serif": ["DejaVu Sans"], "size": 10})
    # Set the font used for MathJax - more on this later
    rc("mathtext", **{"default": "regular"})
    plt.rc("font", family="serif")
    
    data = np.transpose(np.loadtxt('dihedral.dat'))
    time = data[0] / 1000 * 2
    theta = data[1] * 180 / np.pi

    plt.figure()
    plt.scatter(time, theta, s=0.5)
    plt.xlabel('Time (ns)')
    plt.ylabel('Dihedral (deg)')
    plt.grid()
    plt.savefig('scatter_dihedral_state_B.png', dpi=600)


