import os
import numpy as np

if __name__ == "__main__":
    data = np.transpose(np.loadtxt('fes.dat'))
    theta, f = data[0], data[1]
    f_min, theta_min = [], []
    for k in range(1, len(f) - 1):
        if f[k - 1] > f[k] and f[k + 1] > f[k]:
            f_min.append(f[k])
            theta_min.append(theta[k])

    data = np.transpose(np.loadtxt('COLVAR'))
    t, theta = data[0][::50], data[1][::50]

    for i in range(len(f_min)):
        shifted_theta = np.abs(theta - theta_min[i])
        min_idx = list(shifted_theta).index(np.min(shifted_theta))
        
        print(f'Minimum {i + 1} is at {theta_min[i]} (f = {f_min[i]} kT).')
        print(f'Closet configuration is at {t[min_idx]} ps, whose dihedral is {theta[min_idx]}.')
        print("Extracting the configurations ...\n")
        os.system(f'echo 0 | gmx trjconv -f *xtc -s *tpr -o sys2_min_{i + 1}.gro -dump {int(t[min_idx])}')

