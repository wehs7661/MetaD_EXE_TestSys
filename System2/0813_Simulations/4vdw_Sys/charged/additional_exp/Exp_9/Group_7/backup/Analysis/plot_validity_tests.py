import matplotlib.pyplot as plt 
from matplotlib import rc 
import numpy as np

if __name__ == "__main__":
    rc("font", **{"family": "sans-serif", "sans-serif": ["DejaVu Sans"], "size": 10})
    # Set the font used for MathJax - more on this later
    rc("mathtext", **{"default": "regular"})
    plt.rc("font", family="serif")

    # Plot the p-values obtained from the strict tests
    p_values = []
    for i in range(5):
        f = open(f'results_strict_{i}.txt', 'r')
        lines = f.readlines()
        f.close()

        data = lines[-1].split('[')[1].split(']')[0].split(',')
        p_data = [float(data[i]) for i in range(len(data))]
        p_values.append(p_data)
    
    p_values = np.transpose(p_values)
    labels = ['Total', 'Translational', 'Rot & Int', 'Rotational', 'Internal']

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    for i in range(5):
        plt.plot(range(1, 6), p_values[i], label=labels[i])
    ax.set_yscale('log')
    plt.xlabel('Time interval')
    plt.ylabel('p-values')
    plt.title('Experimental 9, Group 8')
    plt.grid()
    plt.legend()
    plt.savefig('p_values_results.png', dpi=600)

    # Plot the temperatures obtained from non-strict tests
    T_mu, T_sigma, T_mu_err, T_sigma_err = [], [], [], []
    for i in range(5): 
        T_mu_data, T_sigma_data = [], []
        T_mu_err_data, T_sigma_err_data = [], []
        T_ref = 298

        f = open(f'results_non-strict_{i}.txt', 'r')
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

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    for i in range(5):
        plt.errorbar(range(1, 6), T_mu[i], yerr=T_mu_err[i], label=labels[i])
    plt.xlabel('Time interval')
    plt.ylabel('T_mu')
    plt.title('Experimental 9, Group 8')
    plt.grid()
    plt.legend()
    plt.savefig('T_mu_results.png', dpi=600)    

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    for i in range(5):
        plt.errorbar(range(1, 6), T_sigma[i], yerr=T_sigma_err[i], label=labels[i])
    plt.xlabel('Time interval')
    plt.ylabel('T_sigma')
    plt.title('Experimental 9, Group 8')
    plt.grid()
    plt.legend()
    plt.savefig('T_sigma_results.png', dpi=600)    

