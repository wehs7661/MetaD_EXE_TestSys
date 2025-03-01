import os
import sys
import glob
import pymbar
import natsort
import argparse
import time as time
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib import cm
from pymbar.timeseries import detectEquilibration
from alchemlyb.parsing.gmx import extract_dHdl, extract_u_nk
from alchemlyb.preprocessing import equilibrium_detection
from alchemlyb.estimators import BAR, MBAR, TI


def initialize(args):
    parser = argparse.ArgumentParser(
        description='This code analyzes the dhdl files generated by replica \
                    exchange molecular dynamics (REMD) simulations to perform \
                    free energy calculations, plot overlap matrices and estimate\
                    the Wang-Landau weights for expanded ensemble.')
    parser.add_argument('-d',
                        '--dir',
                        type=str,
                        default='.',
                        help='The directory where the dhdl files are.')
    parser.add_argument('-T',
                        '--temp',
                        type=float,
                        default=298.15,
                        help='The temperature in Kelvin the simulation was performed at.')
    parser.add_argument('-dt',
                        '--dt',
                        type=float,
                        default=0.2,
                        help='The time step used in the dhdl files')
    parser.add_argument('-s',
                        '--spacing',
                        type=float,
                        help='The spacing in time (ns) to plot the free energy estimate as a function of time.')
    parser.add_argument('-t',
                        '--time',
                        type=float,
                        help='The length of the simulation to be considered.')
    args_parse = parser.parse_args(args)

    return args_parse

def ordinal(n):
    ordinal_str = "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
    return ordinal_str

class Preprocessing():
    def __init__(self):
        pass

    def extract_data(self, dir, temp, dt, time=None):
        # extract and subsample dHdl using equilibrium_detection
        dHdl_state = []  # dHdl_state is for collecting data for a single state
        u_nk_state = []  # u_nk_state is for collecting data fro a single state

        if os.path.isfile('temporary.xvg') is True:
            os.system("rm temporary.xvg")
        files = glob.glob(os.path.join(dir, '*dhdl.xvg*'))
        files = natsort.natsorted(files, reverse=False)

        file_idx = -1  
        n = 0     # counter for the number of files of a specific state
        self.n_state = 0   # counter for the number of states
        
        for i in files:
            n += 1
            file_idx += 1 
            logger(f"Parsing {files[file_idx]} and collecting data ...")
            os.system(f"head -n-1 {i} > temporary.xvg")  # delete the last line in case it is incomplete
            if time is not None:
                dHdl_state.append(extract_dHdl('temporary.xvg', T=temp).loc[:time])
                u_nk_state.append(extract_u_nk('temporary.xvg', T=temp).loc[:time])
            else:
                dHdl_state.append(extract_dHdl('temporary.xvg', T=temp))
                u_nk_state.append(extract_u_nk('temporary.xvg', T=temp))
            
            if n > 1:  # for discard the overlapped time frames of the previous file
                upper_t = dHdl_state[-2].iloc[dHdl_state[-2].shape[0] - 1].name[0]   # the last time frame of file n
                lower_t = dHdl_state[-1].iloc[0].name[0]   # the first time frame of file n + 1 
                # upper_t and lower_t should be the same for both dHdl and u_nk

                if lower_t != 0:   # in case that the file n+1 is the first file of the next replica
                    n_discard = int((upper_t - lower_t) / dt + 1)   # number of data frames to discard in file n
                    dHdl_state[-2] = dHdl_state[-2].iloc[:-n_discard]
                    u_nk_state[-2] = u_nk_state[-2].iloc[:-n_discard]
                else:  # lower_t == 0 means that we have gathered dHdl for the previous state
                    self.n_state += 1
                    dHdl_data = pd.concat(dHdl_state[:-1])
                    u_nk_data = pd.concat(u_nk_state[:-1])

                    dHdl.append(equilibrium_detection(dHdl_data, dHdl_data.iloc[:, 0]))
                    dHdl_state = [dHdl_state[-1]]
                    logger(f'Subsampling dHdl data of the {ordinal(self.n_state)} state ...')

                    u_nk.append(equilibrium_detection(u_nk_data, u_nk_data.iloc[:, 0]))
                    u_nk_state = [u_nk_state[-1]]
                    logger(f'Subsampling u_nk data of the {ordinal(self.n_state)} state ...')

                    n = 1   # now there is only one file loaded in dHdl_state/u_nk_state

        # dealing with the last state with equilibrium_detection
        self.n_state += 1
        dHdl_data = pd.concat(dHdl_state)
        u_nk_data = pd.concat(u_nk_state)

        return dHdl_data, u_nk_data

    def decorrelate_data(self, dHdl_data=None, u_nk_data=None):
        dHdl, u_nk = [], []
        if dHdl_data is not None:
            dHdl.append(equilibrium_detection(dHdl_data, dHdl_data.iloc[:, 0]))
            #logger(f'Subsampling dHdl data of the {ordinal(self.n_state)} state ...')
            _, g1, _ = detectEquilibration(dHdl_data.iloc[:, 0].values)
            dHdl = pd.concat(dHdl)
            setattr(dHdl, 'statineff', g1)
        
        if u_nk_data is not None:
            u_nk.append(equilibrium_detection(u_nk_data, u_nk_data.iloc[:, 0]))
            #logger(f'Subsampling u_nk data of the {ordinal(self.n_state)} state ...\n')
            t2, g2, N2 = detectEquilibration(u_nk_data.iloc[:, 0].values)
            u_nk = pd.concat(u_nk)
            setattr(u_nk, 'statineff', g2)

        logger("Data preprocessing completed!\n")
        if os.path.isfile('temporary.xvg') is True:
            os.system("rm temporary.xvg")

        return dHdl, u_nk

def free_energy_evolution(u_nk_data, spacing):
    """
    This function calculates free energy difference between the coupled and 
    uncoupled state as well as their uncertainties as a function of time using MBAR. 
    
    Parameters
    ----------
    spacing : float
        The spacing in time (ns) that we use to extract subsets for plotting
        free energy as a function of time. For example, if spacing = 2, the 
        data of first 2, 4, 6, ... ns will be used to calculate the free energy 
        difference. Note that the calculation based on the whole dataset is the 
        job of the function free_energy_calculation and we don't do it here.
    """
    
    t_final = u_nk_data.index[-1][0]
    if t_final % (spacing * 1000) == 0:
        n_subset = int(t_final / (spacing * 1000)) - 1
    else:
        n_subsets = int(np.floor(t_final / (spacing * 1000))) # number of subsets
    t = list(np.arange(spacing, t_final / 1000, spacing))  # time
    t.append(t_final / 1000)

    f, std = [], []  # free energy difference and the standard deviation
    for i in range(n_subsets):
        # First, we have to decorrelate the subset of data
        print(f'Data analysis of the first {(i + 1) * spacing} ns of the u_nk data ...')
        u_nk_subset = []   # u_nk.loc[596] is the subset of the data before 596 ps
        u_nk_subset.append(equilibrium_detection(u_nk_data.loc[:(i+1) * 1000 * spacing], u_nk_data.loc[:(i+1) * 1000 * spacing].iloc[:, 0]))
        u_nk_subset = pd.concat(u_nk_subset)
        
        # Then, we do free energy calculation on the subset using MBAR
        try: 
            mbar_stop = False
            mbar = MBAR().fit(u_nk_subset)   
        except pymbar.utils.ParameterError:
            mbar_stop = True
            logger("\sum_n W_nk is not equal to 1, probably due to insufficient overlap between states.")
            logger("Stop using MBAR ...")

        f.append(mbar.delta_f_.iloc[0, -1])
        std.append(mbar.d_delta_f_.iloc[0, -1])

    return f, std, t

def free_energy_calculation(dHdl, u_nk):
    logger("Fitting TI on dHdl ...")
    ti = TI().fit(dHdl)

    logger("Fitting BAR on u_nk ...")
    bar = BAR().fit(u_nk)

    logger("Fitting MBAR on u_nk ...\n")
    
    try:
        mbar_stop = False
        mbar = MBAR().fit(u_nk)
    except pymbar.utils.ParameterError:
        mbar_stop = True
        logger("\sum_n W_nk is not equal to 1, probably due to insufficient overlap between states.")
        logger("Stop using MBAR ...")
    
    logger("------ Results based on the whole dataset ------")
    if hasattr(dHdl, 'statineff') is True:
        logger(f'Statistical inefficiency of dHdl: {dHdl.statineff}')
    if hasattr(u_nk, 'statineff') is True:
        logger(f'Statistical inefficiency of u_nk: {u_nk.statineff}\n')
    logger(f"TI: {ti.delta_f_.iloc[0, -1]} +/- {ti.d_delta_f_.iloc[0, -1]} kT")
    logger(f"BAR: {bar.delta_f_.iloc[0, -1]} +/- unknown kT")
    if mbar_stop is False:
        logger(f"MBAR: {mbar.delta_f_.iloc[0, -1]} +/- {mbar.d_delta_f_.iloc[0, -1]} kT")
        logger("------------------------------------------------")
        return ti, bar, mbar
    else:
        logger("------------------------------------------------")
        return ti, bar

def get_overlap_matrix(u_nk):
    # sort by state so that rows from same state are in contiguous blocks
    u_nk = u_nk.sort_index(level=u_nk.index.names[1:])

    groups = u_nk.groupby(level=u_nk.index.names[1:])
    N_k = [(len(groups.get_group(i)) if i in groups.groups else 0) for i in u_nk.columns]        
    solver_options = {"maximum_iterations":10000,"verbose":True}
    solver_protocol = {"method":"adaptive","options":solver_options}
    MBAR = pymbar.mbar.MBAR(u_nk.T, N_k, solver_protocol=(solver_protocol,))
    results = MBAR.getFreeEnergyDifferences()
    print(results)
    overlap_matrix = np.array(MBAR.computeOverlap()['matrix'])

    return overlap_matrix

def plot_matrix(matrix, png_name, start_idx=0):
    sns.set_context(rc={
    'family': 'sans-serif',
    'sans-serif': ['DejaVu Sans'],
    'size': 5
    })

    K = len(matrix)
    plt.figure(figsize=(K / 3, K / 3))
    annot_matrix = np.zeros([K, K])   # matrix for annotating values

    mask = []
    for i in range(K):
        mask.append([])
        for j in range(len(matrix[0])):
            if matrix[i][j] < 0.005:            
                mask[-1].append(True)
            else:
                mask[-1].append(False)

    for i in range(K):
        for j in range(K):
            annot_matrix[i, j] = round(matrix[i, j], 2)

    x_tick_labels = y_tick_labels = np.arange(start_idx, start_idx + K)
    ax = sns.heatmap(matrix, cmap="YlGnBu", linecolor='silver', linewidth=0.25,
                    annot=annot_matrix, square=True, mask=matrix<0.005, fmt='.2f', cbar=False, xticklabels=x_tick_labels, yticklabels=y_tick_labels)
    ax.xaxis.tick_top()
    ax.tick_params(length=0)
    cmap = cm.get_cmap('YlGnBu')   # to get the facecolor
    ax.set_facecolor(cmap(0))      # use the brightest color (value = 0)
    for _, spine in ax.spines.items():
        spine.set_visible(True)    # add frames to the heat map
    plt.annotate('$\lambda$', xy=(0, 0), xytext=(-0.45, -0.20))
    plt.title('Overlap matrix', fontsize=10, weight='bold')
    plt.tight_layout(pad=1.0)

    plt.savefig(png_name, dpi=600)
    #plt.show()
    plt.close()

def logger(*args, **kwargs):
    print(*args, **kwargs)
    with open("Result.txt", "a") as f:
        print(file=f, *args, **kwargs)

if __name__ == "__main__":

    rc('font', **{
        'family': 'sans-serif',
        'sans-serif': ['DejaVu Sans'],
        'size': 6
    })
    # Set the font used for MathJax - more on this later
    rc('mathtext', **{'default': 'regular'})
    plt.rc('font', family='serif')

    t1 = time.time()
    args = initialize(sys.argv[1:])
  
    logger('Preprocessing the data in the dhdl files ...')
    preprocessing = Preprocessing()
    dHdl_data, u_nk_data = preprocessing.extract_data(args.dir, args.temp, dt=args.dt, time=args.time)    
    dHdl, u_nk = preprocessing.decorrelate_data(dHdl_data, u_nk_data)

    logger("\nPerforming free energy calculations on the whole dataset ...")
    
    output = free_energy_calculation(dHdl, u_nk)  # output[0] = ti, output[1] = bar, output[2] = mbar (if any)
    
    if args.spacing is not None:
        logger("\nCalculating the free energy difference between the coupled and uncoupled state")
        logger("as a function of time using MBAR ...")
        f, std, t = free_energy_evolution(u_nk_data, args.spacing)
        if len(f) != 0:  # append the results based on the whole subset
            f.append(output[2].delta_f_.iloc[0, -1])
            std.append(output[2].d_delta_f_.iloc[0, -1])
    
        # plot the free energy difference as a function of time (with error bars)
        rc('font', **{'size': 10})  # change the font size
        plt.rc('font', family='serif')
        plt.figure()
        plt.plot(t, f)
        f, std = np.array(f), np.array(std)
        plt.fill_between(t, f - std, f + std, color='lightskyblue')
        plt.xlabel('Time (ns)')
        plt.ylabel('Free energy difference btw. the end state ($ k_{B}T$)')
        plt.title('Free energy as a function of time')
        plt.grid()
        # plt.show()
        plt.savefig("free_energy_evolution.png", dpi=600)

        # plot the uncertainty as a function of time
        plt.figure()
        plt.plot(t, std)
        plt.xlabel('Time (ns)')
        plt.ylabel('Uncertainty of the free energy difference ($ k_{B}T$)')
        plt.title('Uncertainty as a function of time')
        plt.grid()
        # plt.show()
        plt.savefig("uncertainty_evolution.png", dpi=600)

    logger("Calculating Wang-Landau weights for expanded ensemble using MBAR ...")
    WL_weights = ""
    """
    logger(ti.delta_f_)
    logger(ti.delta_f_.iloc[0])
    logger(ti.delta_f_.iloc[0][0])
    logger(ti.delta_f_.iloc[0][1])
    logger(ti.delta_f_.iloc[0][2])
    
    
    for i in range(len(output[1].delta_f_.iloc[0])):
        WL_weights += (' ' + str(round(output[1].delta_f_.iloc[0][i], 5)))
    logger('Estimated Wang-Landau weights by BAR: %s' % WL_weights)
    """
    logger("\nComputing and visualizing the overlap matrix ...")
    matrix = get_overlap_matrix(u_nk)
    #print(matrix)
    plot_matrix(matrix, 'overlap_matrix.png')
    t2 = time.time()
    logger(f"Time elapsed: {t2 - t1} seconds.")



