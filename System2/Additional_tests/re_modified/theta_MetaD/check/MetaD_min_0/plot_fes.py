import glob
import natsort 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc

def extract_fes(input_f):
    theta, fes = [], []
    f = open(input_f, 'r')
    lines = f.readlines()
    f.close()

    theta, fes = [], []
    for l in lines:
        if l[0] != '#' and l[0] != '@':
            theta.append(float(l.split()[0]))
            fes.append(float(l.split()[1]))

    theta = np.array(theta) * 180 / np.pi
    fes = np.array(fes) / 2.478956208925815

    return theta, fes

def find_left_min(theta, fes):
    fes = fes[theta < 0]
    f_min = np.min(fes)
    theta_min = theta[list(fes).index(f_min)]

    return f_min, theta_min

if __name__ == '__main__':
    # Plotting the results if needed
    rc('font', **{
       'family': 'sans-serif',
       'sans-serif': ['DejaVu Sans'],
       'size': 10
    })
    # Set the font used for MathJax - more on this later
    rc('mathtext', **{'default': 'regular'})
    plt.rc('font', family='serif')

    files = glob.glob('fes_*.dat')
    files = natsort.natsorted(files)

    plt.figure()
    f_min_list, theta_min_list = [], []
    for i in range(len(files)):
        theta, fes = extract_fes(files[i])
        f_min, theta_min = find_left_min(theta, fes)
        f_min_list.append(f_min)
        theta_min_list.append(theta_min)

        if i < len(files) - 1:
            plt.plot(theta, fes, label=f'{5 * (i + 1)} ns', linestyle='--')
        else:
            plt.plot(theta, fes, label=f'{5 * (i + 1)} ns')
    
    plt.xlabel('Dihedral angle (deg)')
    plt.ylabel('Free energy ($ k_{B}T $)')
    plt.title('Free energy as a function of dihedral angle')
    plt.grid()
    plt.legend()
    plt.savefig('sys2_fes_angle_max.png', dpi=600)

    t = np.array([(i + 1) * 0.5 for i in range(len(theta_min_list))])    
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot(t, f_min_list, 'b-')
    ax2.plot(t, theta_min_list, 'r-')

    ax1.set_xlabel('Time (ns)')
    ax1.set_ylabel('The left minimum ($ k_{B}T $)', color='b')
    ax2.set_ylabel('The position of the left minimum (deg)', color='r')
    plt.grid()
    plt.tight_layout()
    plt.savefig('sys2_mininfo_angle_max.png', dpi=600)

    print(f'At the end of the simulation, the left free energy minimum is {f_min_list[-1]}, which is at {theta_min_list[-1]} degrees.')
