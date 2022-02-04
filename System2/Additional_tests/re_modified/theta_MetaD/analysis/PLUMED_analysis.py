import os
import numpy as np

def logger(*args, **kwargs):
    print(*args, **kwargs)
    abspath = '/home/wei-tse/Documents/MetaD_EXE_TestSys/System2/Additional_tests/re_modified/theta_MetaD'
    with open(f"{abspath}/PLUMED_analysis_results.txt", "a") as f:
        print(file=f, *args, **kwargs)

if __name__ == '__main__':
    logger(f'========== Data analysis ==========')
    os.chdir('../')

    # Task 1
    logger('Generating fes.dat and plotting the free energy profile ...')
    os.system('plumed sum_hills --hills HILLS --bin 100 --mintozero')
    os.system(f'plot_2d -f fes.dat -x "Torsional angle relevant to the H.B. (degree)" -y "Free energy (kT)" -t "Torsional angle as a function of time" -n fes_remodified_sys2 -cx "radian to degree" -cy "kJ/mol to kT"')
    # Task 2-1: Get the local minima of free energy 
    data = np.loadtxt('fes.dat')
    theta = np.array([data[x][0] for x in range(len(data))])
    f = np.array([data[x][1] for x in range(len(data))]) # units: kJ/mol
    c2 = 2.4777090399459767
    f = f / c2   # units: kT
    f_min, theta_min = [], []   # local minima
    for k in range(1, len(f) - 1):
        if f[k - 1] > f[k] and f[k + 1] > f[k]:
            f_min.append(f[k])
            theta_min.append(theta[k])
    logger(f'Number of local minimum/minima of the free energy profile: {len(f_min)}')

    # Task 2-2: Estimate the free energy barrier
    c = 180 / np.pi
    for k in range(1, len(f) - 1):
        if f[k - 1] < f[k] and f[k + 1] < f[k] and theta[k] * c < 100 and theta[k] * c > -100:
            f_max = f[k]
            theta_max = theta[k]
    logger(f'The free energy barrier starting from state 1: {f_max - f_min[0]} kT.')

    # Task 2-3: Find the time frames corresponding to the minima 
    CV_series = np.loadtxt('COLVAR')
    CV = np.array([CV_series[x][1] for x in range(len(CV_series))])
    time = np.array([CV_series[x][0] for x in range(len(CV_series))])
    t_min = []
    for k in theta_min:
        diff = list(np.abs(CV - k))
        t_min.append(time[diff.index(min(diff))])  # units: ps


    for k in range(len(f_min)):
        logger(f'Local minimum {k + 1}: at theta = {theta_min[k]}, f = {f_min[k]} (closest time frame: at {t_min[k]} ps, theta = {CV[list(time).index(t_min[k])]})')

        # Task 2-3: Extract the configurations at the energy minima
        logger('Extracting the corresponding configruation ...')
        os.system(f'echo 0 | gmx trjconv -f sys2.xtc -s sys2.tpr -o sys2_min_{k}.gro -dump {t_min[k]}')

    # Task 3: Plot the CV as a function of time
    logger('Plotting the CV as a function of time ...')
    os.system(f'plot_2d -f COLVAR -y "Torsional angle relevant to the H.B. (degree)" -x "Time (ps)" -t "Torsional angle as a function of time" -n dihedral_remodified_sys2 -cy "radian to degree"')
