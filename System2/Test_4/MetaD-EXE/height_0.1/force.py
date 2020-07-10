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

f = open('force.xvg', 'r')
lines = f.readlines()
f.close()

force, time = [], []
for i in range(12):
    force.append([])

for l in lines:
    if l[0] != '#' and l[0] != '@':
        data = [float(d) for d in l.split()]
        total_force = [data[3 * i + 1] ** 2 + data[3 * i + 2] ** 2 + data[3 * i + 3] ** 2 for i in range(12)]
        time.append(data[0])
        for i in range(12):
            force[i].append(total_force[i])

plt.figure()
for i in range(12):
    plt.plot(time, force[i], label=f'Atom {i}')
plt.xlabel('Time (ps)')
plt.ylabel('Force ($kJ mol^{-1} nm^{-1}$)')
plt.title('Force as a function of time')
plt.grid()
plt.legend()
plt.savefig('force_time.png', dpi=600)









