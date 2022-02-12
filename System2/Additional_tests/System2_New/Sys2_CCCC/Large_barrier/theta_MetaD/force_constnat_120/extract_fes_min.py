import os
import numpy as np

class Logging:
    def __init__(self, file_name):
        self.f = file_name

    def logger(self, *args, **kwargs):
        """
        Prints the results on screen and to the file free_energy_results.txt

        Parameters
        ---------
        file_name (str): The file name of the output.
        """
        print(*args, **kwargs)
        with open(self.f, "a") as f:                                        
            print(file=f, *args, **kwargs)

if __name__ == "__main__":
    L = Logging('extract_min_results.txt')
    data = np.transpose(np.loadtxt('fes.dat'))
    theta, f = data[0], data[1]
    f_min, theta_min = [], []

    for k in range(0, len(f) - 1):
        """
        if k == 0:
            if f[k] == np.min(f):
                print('no')
                f_min.append(f[k])
                theta_min.append(theta[k])
        """
        if f[k - 1] > f[k] and f[k + 1] > f[k]:
            f_min.append(f[k])
            theta_min.append(theta[k])

    data = np.transpose(np.loadtxt('COLVAR'))
    t, theta = data[0][::50], data[1][::50]

    for i in range(len(f_min)):
        shifted_theta = np.abs(theta - theta_min[i])
        min_idx = list(shifted_theta).index(np.min(shifted_theta))
        
        L.logger(f'Minimum {i + 1} is at {theta_min[i]} (f = {f_min[i]} kT).')
        L.logger(f'Closet configuration is at {t[min_idx]} ps, whose dihedral is {theta[min_idx]}.')
        L.logger("Extracting the configurations ...\n")
        os.system(f'echo 0 | gmx trjconv -f *xtc -s *tpr -o sys2_min_{i + 1}.gro -dump {int(t[min_idx])}')

