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

N, Lambda = [], []
infile = open('COLVAR', 'r')
lines = infile.readlines()
infile.close()

for line in lines:
    if line[0] != '#' and line[0] != '@' and len(line.split()) == 4:
        N.append(float(line.split()[1]))
        Lambda.append(float(line.split()[2]))

plt.figure()
plt.scatter(N, Lambda, marker='x', s=0.5)
plt.xlabel('The number of water molecules in the cavity')
plt.ylabel('The index of the alchemical state')
plt.grid()
plt.savefig('diffusion_2d.png', dpi=600)
