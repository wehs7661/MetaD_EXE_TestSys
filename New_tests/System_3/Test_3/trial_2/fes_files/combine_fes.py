import numpy as np 
import ruptures as rpt 
import matplotlib.pyplot as plt 
from matplotlib import rc

if __name__ == "__main__":
    fes_1D = np.load('df_1D.npy')
    fes_2D = np.load('df_2D.npy')
    fes_combined = fes_1D + fes_2D

    rc('font', **{
        'family': 'sans-serif',
        'sans-serif': ['DejaVu Sans'],
        'size': 10,
        'weight': 'bold',
    })
    # Set the font used for MathJax - more on thiprint(images)
    rc('mathtext', **{'default': 'regular'})
    plt.rc('font', family='Arial')

    algo = rpt.Window(width=50, model='l2').fit(np.array(fes_combined))
    change_loc = algo.predict(n_bkps=10)
    change_t = np.array(change_loc) * 20 / 1000

    t = (np.arange(10000) + 1) * 20 / 1000

    plt.figure()
    plt.plot(t, fes_combined)
    for i in change_t:
        plt.axvline(i, lw=1, color='red')
    plt.xlabel('Time (ns)')
    plt.ylabel('Free energy difference (kT)')
    plt.grid()
    plt.savefig(f'fes_timeseries_combined.png', dpi=600)
