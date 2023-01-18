import plumed 
import numpy as np
import ruptures as rpt
import matplotlib.pyplot as plt
from matplotlib import rc

if __name__ == '__main__':
    rc("font", **{"family": "sans-serif", "sans-serif": ["DejaVu Sans"], "size": 10})
    # Set the font used for MathJax - more on this later
    rc("mathtext", **{"default": "regular"})
    plt.rc("font", family="Arial")

    data = plumed.read_as_pandas('analysis.dat')
    t = np.array(data['time']) / 1000
    n = np.array(data['n'])
    
    """
    algo = rpt.Window(width=40, model="l2").fit(n)
    change_loc = algo.predict(n_bkps=10)
    """

    plt.figure()
    plt.plot(t, n)
    """
    for i in change_loc:
        print(f'Marking the change location at {t[i-1]} ns ...')
        plt.axvline(t[i-1], lw=2, color='red')
    """
    plt.ylim([0, 13.5])
    plt.xlabel('Time (ns)')
    plt.ylabel('Number of water molecules')
    plt.grid()
    plt.savefig('test.png', dpi=600)
    # plt.savefig('water_timeseries_1D.png', dpi=600)
