import pickle
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

pickle_1 = 'MetaD_EXE/rerun/final_hist.pickle'
pickle_2 = 'EXE_fixed/analysis/final_hist.pickle'

with open(pickle_1, 'rb') as handle:
    data_1 = pickle.load(handle)  # final_counts = data_1[0]
with open(pickle_2, 'rb') as handle:
    data_2 = pickle.load(handle)  # final_counts = data_2[0]

# set width of bar
bar_width = 0.30
 
# Set position of bar on X axis
r1 = np.arange(1, 7) - bar_width / 2
r2 = np.array([x + bar_width for x in r1])

# Plot the final histogram
plt.figure()
plt.bar(r1, height=data_1[0], width = bar_width, label='Experimental group')
plt.bar(r2, height=data_2[0], width = bar_width, label='Control group')
plt.xlabel('States')
plt.ylabel('Counts')
plt.minorticks_on()
plt.title('The final histogram of the simulation (at 5 ns)')
if max(data_1[0]) >= 10000:
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
plt.grid()
plt.legend()
plt.savefig('Compare_final_hist.png', dpi=600)
