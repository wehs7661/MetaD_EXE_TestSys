import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc

rc('font', **{
'family': 'sans-serif',
'sans-serif': ['DejaVu Sans'],
'size': 10
})
# Set the font used for MathJax - more on this later
rc('mathtext', **{'default': 'regular'})
plt.rc('font', family='serif')

data = np.loadtxt("sum_hills_data.txt")
fes_series = np.array([data[i][1] for i in range(501)])

plt.figure()
plt.plot(np.linspace(4000, 5000, 501), fes_series)
plt.xlabel('Time (ps)')
plt.ylabel('Free energy difference ($ k_{B}T $)')
plt.title('The free energy difference as a function of time')
plt.grid()
plt.savefig('free_energy_evolution.png', dpi=600)