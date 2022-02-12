import time
import os
import glob
import physical_validation
import contextlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc

def plot_temp(temp, temp_err, labels, lambdas, ylabel):
    fig = plt.figure(figsize=(16, 8))
    ax1 = fig.add_subplot(1, 1, 1)
    ax2 = ax1.twiny()
    fig.subplots_adjust(bottom=0.2)

    for i in range(5):
        plt.errorbar(range(1, 21), temp[i], yerr=temp_err[i], label=labels[i])

    ax1.spines["bottom"].set_position(("axes", -0.08))
    ax1.set_xticks(range(1, 21))
    ax1.set_xlim([0, 21])
    ax1.set_xticklabels([str(i) for i in lambdas])
    ax1.set_ylabel(ylabel)
    ax1.tick_params(axis=u'both', which=u'both',length=0)
    ax1.grid()
    plt.legend()

    ax2.set_xticks(range(1, 21))
    ax2.set_xlim([0, 21])
    ax2.set_xticklabels(range(1, 21))
    ax2.set_frame_on(True)
    ax2.patch.set_visible(False)
    ax2.xaxis.set_ticks_position("bottom")
    ax2.xaxis.set_label_position("bottom")

    ax1.text(1.02, -0.11, '$ \lambda_{coul} $', fontsize=12, weight='bold', transform=ax1.transAxes)
    ax1.text(1.02, -0.15, '$ \lambda_{vdw} $', fontsize=12, weight='bold', transform=ax1.transAxes)
    plt.tight_layout()
    plt.savefig(f'{ylabel}_results.png', dpi=600)


if __name__ == "__main__":
    t1 = time.time()
    run_test = False
    
    if run_test is True:
        bools = [True, False]
        test_type = ['strict', 'non-strict']

        for i in range(1, 21):
            if len(glob.glob(f'Group_{i}/Analysis/*trr')) < 1:
                os.system(f"cd Group_{i}/Analysis && echo 2 | gmx trjconv -s ../*tpr -f ../*trr -o sys2_cccc_lig.trr")
    
            for j in range(len(test_type)):
                print(f'\nRunning {test_type[j]} test for Group {i} ...')
                parser = physical_validation.data.GromacsParser()
    
                res = parser.get_simulation_data(
                mdp=f'Group_{i}/mdout.mdp',
                top=f'Group_{i}/Analysis/sys2_cccc_lig.top',
                edr=f'Group_{i}/sys2_cccc.edr',
                trr=f'Group_{i}/Analysis/sys2_cccc_lig.trr'
                )

                res.system.ndof_reduction_tra = 0

                with open(f'Group_{i}/Analysis/results_{test_type[j]}.txt', 'w') as f:
                    with contextlib.redirect_stdout(f):
                        results = physical_validation.kinetic_energy.equipartition(
                            data=res,
                            strict=bools[j],
                            filename=f'group_{i}_{test_type[j]}',
                        )
                        f.write(str(results))
            os.system(f'cd Group_{i}/Analysis && mkdir Strict Non_Strict')
            os.system(f'mv *_strict* Group_{i}/Analysis/Strict/.')
            os.system(f'mv *non-strict* Group_{i}/Analysis/Non_Strict/.')
            os.system(f'mv Group_{i}/Analysis/*_strict* Group_{i}/Analysis/Strict/.')
            os.system(f'mv Group_{i}/Analysis/*non-strict* Group_{i}/Analysis/Non_Strict/.')


    # plot the figures
    rc("font", **{"family": "sans-serif", "sans-serif": ["DejaVu Sans"], "size": 10})
    # Set the font used for MathJax - more on this later
    rc("mathtext", **{"default": "regular"})
    plt.rc("font", family="serif")

    coul = [0.00, 0.05, 0.10, 0.20, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60, 0.70, 0.85, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00]
    vdw = [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.20, 0.40, 0.50, 0.60, 0.70, 0.80, 1.00]
    lambdas = [f'{coul[i]}\n\n{vdw[i]}' for i in range(len(coul))]

    p_values = []
    for i in range(1, 21):
        f = open(f'Group_{i}/Analysis/Strict/results_strict.txt', 'r')
        lines = f.readlines()
        f.close()

        data = lines[-1].split('[')[1].split(']')[0].split(',')
        p_data = [float(data[i]) for i in range(len(data))]
        p_values.append(p_data)

    p_values = np.transpose(p_values)
    labels = ['Total', 'Translational', 'Rot & Int', 'Rotational', 'Internal']

    fig = plt.figure(figsize=(16, 8))
    ax1 = fig.add_subplot(1, 1, 1)
    ax2 = ax1.twiny()
    fig.subplots_adjust(bottom=0.2)

    for i in range(5):
        plt.plot(range(1, 21), p_values[i], label=labels[i], marker='.')
    
    ax1.fill_between([0, 21], 0.05, 10, color='lightgreen', alpha=0.3)
    ax1.fill_between([0, 21], 0.05, 0, color='lightblue', alpha=0.3)

    ax1.spines["bottom"].set_position(("axes", -0.08))
    ax1.set_xticks(range(1, 21))
    ax1.set_xlim([0, 21])
    ax1.set_ylim([10**(-31), 10])
    ax1.set_xticklabels([str(i) for i in lambdas])
    ax1.set_yscale('log')
    ax1.set_ylabel('p-values')
    ax1.tick_params(axis=u'both', which=u'both',length=0)
    ax1.grid()
    plt.legend()
    
    ax2.set_xticks(range(1, 21))
    ax2.set_xlim([0, 21])
    ax2.set_ylim([10**(-31), 10])
    ax2.set_xticklabels(range(1, 21))
    ax2.set_frame_on(True)
    ax2.patch.set_visible(False)
    ax2.xaxis.set_ticks_position("bottom")
    ax2.xaxis.set_label_position("bottom")

    ax1.text(1.02, -0.11, '$ \lambda_{coul} $', fontsize=12, weight='bold', transform=ax1.transAxes)
    ax1.text(1.02, -0.15, '$ \lambda_{vdw} $', fontsize=12, weight='bold', transform=ax1.transAxes)
    plt.tight_layout()
    plt.savefig('p_values_results.png', dpi=600)

    # plot temperatures
    T_mu, T_sigma, T_mu_err, T_sigma_err = [], [], [], []
    for i in range(1, 21):
        T_mu_data, T_sigma_data = [], []
        T_mu_err_data, T_sigma_err_data = [], []
        T_ref = 298

        f = open(f'Group_{i}/Analysis/Non_Strict/results_non-strict.txt', 'r')
        lines = f.readlines()
        f.close()

        for l in lines:
            if 'T(mu)' in l:
                T_mu_data.append(float(l.split('T(mu) = ')[1].split('+-')[0]))
                T_mu_err_data.append(float(l.split('T(mu) = ')[1].split('+-')[1].split('K')[0]))
            elif 'T(sigma)' in l:
                T_sigma_data.append(float(l.split('T(sigma) = ')[1].split('+-')[0]))
                T_sigma_err_data.append(float(l.split('T(sigma) = ')[1].split('+-')[1].split('K')[0]))

        T_mu.append(T_mu_data)
        T_sigma.append(T_sigma_data)
        T_mu_err.append(T_mu_err_data)
        T_sigma_err.append(T_sigma_err_data)

    T_mu = np.transpose(T_mu)
    T_sigma = np.transpose(T_sigma)
    T_mu_err = np.transpose(T_mu_err)
    T_sigma_err = np.transpose(T_sigma_err)

    plot_temp(T_mu, T_mu_err, labels, lambdas, 'T_mu')  
    plot_temp(T_sigma, T_sigma_err, labels, lambdas, 'T_simga')

    t2 = time.time()
    print(f'Elapsed time: {t2 - t1} seconds.')
