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

theta = list(np.array(theta) * 180 / np.pi)

plt.figure()
plt.scatter(theta[::100], Lambda[::100], marker='x', s=2, c=plt.cm.plasma(np.linspace(0, 1, len(theta[::100]))))
plt.xlabel('Torsional angle relevant to the H.B. (degree)')
plt.ylabel('Index of the alchemical state')
plt.grid()
plt.savefig('diffusion_2d.png', dpi=600)

plt.figure()
ax = plt.axes(projection='3d')
ax.scatter3D(Lambda, theta, np.array(t) / 1000, c=t, cmap='Blues')
ax.set_ylabel('Torsional angle (degree)')
ax.set_xlabel('Index of the alchemical state')
ax.set_zlabel('Time (ns)')
plt.savefig('diffusion_3d.png', dpi=600)



