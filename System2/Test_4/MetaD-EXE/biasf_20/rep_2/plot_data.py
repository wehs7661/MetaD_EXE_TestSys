import numpy as np

A = np.loadtxt('sum_hills_data_redo.txt')
time = np.array([A[i][0] for i in range(len(A))])
f = np.array([A[i][1] for i in range(len(A))])
#f /= 100

import matplotlib.pyplot as plt
from matplotlib import rc

rc('font', **{
    'family': 'sans-serif',
    'sans-serif': ['DejaVu Sans'],
    'size': 10
    })

plt.figure()
plt.plot(time/1000, f)
plt.xlabel('Time (ns)')
plt.ylabel('Free energy difference ($ k_{B} T$)')
plt.title('Free energy difference as a function of time')
plt.grid()
plt.savefig('free_energy_diff_time.png')








