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

t, theta, Lambda = [], [], []
infile = open('COLVAR', 'r')
lines = infile.readlines()
infile.close()

for line in lines:
    if line[0] != '#' and line[0] != '@' and len(line.split()) == 4:
        t.append(float(line.split()[0]))
        theta.append(float(line.split()[1]))
        Lambda.append(float(line.split()[2]))

plt.figure()
plt.scatter(theta[::250], Lambda[::250], s=10.0, c=plt.cm.viridis(np.linspace(0, 1, len(t[::250]))))
plt.xlabel('The dihedral angle related to the intramolecular H.B.')
plt.ylabel('The index of the alchemical state')
# plt.grid()
cbar = plt.colorbar()
cbar.set_ticks(np.linspace(0, 1, 11))
cbar.set_ticklabels(np.arange(0, 24, 2))
plt.savefig('diffusion_2d.png', dpi=600)
