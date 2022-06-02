import plumed 
import numpy as np
import ruptures as rpt
import matplotlib.pyplot as plt
from matplotlib import rc

if __name__ == "__main__":
    rc('font', **{
       'family': 'sans-serif',
       'sans-serif': ['DejaVu Sans'],
       'size': 10
       })
    # Set the font used for MathJax - more on this later
    rc('mathtext', **{'default': 'regular'})
    plt.rc('font', family='serif')

    data = plumed.read_as_pandas('COLVAR')
    n = np.array(data['n'])
    t = np.array(data['time']) / 100  # ns
    
    algo = rpt.Binseg(model="l2").fit(n)
    change_loc = algo.predict(n_bkps=10)

    # algo = rpt.Window(width=40, model='l2').fit(n)
    # change_loc = algo.predict(n_bkps=10)
    
    print(f'The locations of the change point (ns): {t[np.array(change_loc)-1]}')

    plt.figure()
    plt.plot(t, n)
    for i in change_loc:
        plt.axvline(t[i - 1], lw=1, color='red')
    plt.xlabel('Time (ns)')
    plt.ylabel('Number of water molecules')
    plt.grid()

    plt.savefig('water_change_point.png', dpi=600)

