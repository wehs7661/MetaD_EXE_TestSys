import os
import numpy as np 
import plumed 
import matplotlib.pyplot as plt 
from matplotlib import rc

def read_plumed_output(plumed_output):
    """
    This function modifies the given plumed output file if it is corrupted, meaning that
    there might be some duplicates in the time series having the same time frames. If the
    file is not corrupted, this fucntion does nothing but only read in the data. 

    Parameters
    ----------
    plumed_output (str): The filename of the plumed output (such as HILLS or COLVAR files) to be read
    """
    data_original = plumed.read_as_pandas(plumed_output)
    data = data_original[~data_original["time"].duplicated(keep='last')]  # deduplicate time frames
    data = data.dropna()        # drop N/A in case that there is any
    data = data.reset_index()   # reset the index of the data frame, after this an column "index" will be added
    data = data.drop(columns=["index"])    # drop the index column
    if len(data) == len(data_original):
        # The simulation finished without any timeouts or crashing issues.
        pass    # the plumed output file won't be modified and there will be no backup
    else:
        # the data in the plumed output file will be replaced with the deduplicated time series
        backup = plumed_output + '_backup'
        os.system(f'mv {plumed_output} {backup}')
        plumed.write_pandas(data, plumed_output)
    return data

def average_bias(hills, avg_frac):
    """
    Averages the bias over a certain last portion of the simulation. 

    Parameters
    ----------
    hills     (PlumeDataFrame): The data read from HILLS. 
    avg_frac  (int): The fraction of the simulation that the data will be averaged when reweighting.

    Returns
    ----------
    hills_avg (PlumedDataFrame): The time-averaged bias.
    """
    n0 = int(len(hills) * (1 - avg_frac))   # number of data points considered
    # the weights for the first n0 points are 1
    w = np.hstack((np.ones(n0), np.linspace(1, 0, len(hills) - n0)))
    hills_avg = hills.copy()
    hills_avg.height *= w
    return hills_avg


if __name__ == "__main__":
    # Settings for plotting
    rc('font', **{
    'family': 'sans-serif',
    'sans-serif': ['DejaVu Sans'],
    'size': 10
    })
    # Set the font used for MathJax - more on this later
    rc('mathtext', **{'default': 'regular'})
    plt.rc('font', family='serif')

    # User-defined parameters
    avg_frac = 0.4667
    trunc_frac = 0.5333
    k = 1.38064852E-23   # Boltzmann constant
    N_a = 6.02214076E23  # Avogadro's number
    T = 298.15
    kT = k * T * N_a / 1000  # kT in kJ/mol

    # Sum up the bias
    """
    hills_avg = average_bias(read_plumed_output("HILLS_2D"), avg_frac)
    plumed.write_pandas(hills_avg, "HILLS_2D_modified")
    os.system(f'mpirun -np 1 plumed driver --plumed plumed_sum_bias.dat --noatoms')
    """

    # Calculate the unbiasing weights
    traj = read_plumed_output('COLVAR_SUM_BIAS')
    n = int(len(traj) * (1 - trunc_frac))  # number of data points considered
    b1 = np.array(traj["metad.bias"])  
    b2 = np.array(traj['uwall.bias'])
    b3 = np.array(traj['lwall.bias'])
    bias = b1 + b2 + b3
    bias -= np.max(bias)     # avoid overflows
    w = np.exp(bias / kT)    # unbiasing weights for the whole time series
    np.save('weights.npy', w)
    traj['weights'] = w

    # Get COM distance timeseries and plot the reweighted histogram for the coupled state
    traj = traj[-n:]
    coupled_traj = traj[traj['lambda']==0]
    decoupled_traj = traj[traj['lambda']==39]

    plt.figure()
    plt.hist(coupled_traj['d'], bins=200, weights=coupled_traj['weights'])
    plt.xlabel('COM distance')
    plt.ylabel('Reweighted counts')
    plt.title('Reweighted distribution of COM distance at $\lambda=0$')
    plt.grid()
    plt.savefig('COM_dist_reweighted_coupled_150ns.png', dpi=600)

    # Calculate the 99 and 99.99-percentile of the COM-distance for fully coupled state
    hist_data = plt.hist(coupled_traj['d'], bins=2000, weights=coupled_traj['weights'])  # we use more bins here
    freq = hist_data[0]
    freq /= np.sum(freq)   # normalize
    cumsum_freq = np.cumsum(freq)
    d_center = [(hist_data[1][i] + hist_data[1][i+1]) / 2 for i in range(len(hist_data[1]) - 1)]   # bin centers

    d1 = np.interp(0.99, cumsum_freq, d_center)      # 99-percentile
    d2 = np.interp(0.9999, cumsum_freq, d_center)    # 99.99-percentile

    print('For the fully coupled state:')
    print(f'The 99-percentil of the COM distance is {d1} nm.')
    print(f'The 99.99-percentil of the COM distance is {d2} nm.')

    # Get COM distance timeseries and plot the reweighted histogram for the decoupled state
    plt.figure()
    plt.hist(decoupled_traj['d'], bins=200, weights=decoupled_traj['weights'])
    plt.xlabel('COM distance')
    plt.ylabel('Reweighted counts')
    plt.title('Reweighted distribution of COM distance at $\lambda=39$')
    plt.grid()
    plt.savefig('COM_dist_reweighted_decoupled_150ns.png', dpi=600)

    # Calculate the 99 and 99.99-percentile of the COM-distance for the decoupled state
    hist_data = plt.hist(decoupled_traj['d'], bins=2000, weights=decoupled_traj['weights'])  # we use more bins here
    freq = hist_data[0]
    freq /= np.sum(freq)   # normalize
    cumsum_freq = np.cumsum(freq)
    d_center = [(hist_data[1][i] + hist_data[1][i+1]) / 2 for i in range(len(hist_data[1]) - 1)]   # bin centers

    d1 = np.interp(0.99, cumsum_freq, d_center)      # 99-percentile
    d2 = np.interp(0.9999, cumsum_freq, d_center)    # 99.99-percentile

    print('\nFor the fully decoupled state')
    print(f'The 99-percentil of the COM distance is {d1} nm.')
    print(f'The 99.99-percentil of the COM distance is {d2} nm.')

