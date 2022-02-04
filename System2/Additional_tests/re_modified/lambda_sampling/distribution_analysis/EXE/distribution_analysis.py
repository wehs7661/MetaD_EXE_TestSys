import os 
import time
import glob 
import natsort
import argparse
import numpy as np 
import matplotlib.pyplot as plt 
from matplotlib import rc 

def initialize():
    parser = argparse.ArgumentParser(
        description='This code plots the angle and dihedral angle distribution for the modified System 2.')
    parser.add_argument('-r',
                        '--rerun',
                        default=False,
                        action='store_true',
                        help='Whether to rerun the plumed driver or not.')
    
    args_parse = parser.parse_args()

    return args_parse


def get_atom_indices(top_file):
    """
    Gets the atom indices of all angles/dihedrals from a topology file.

    Parameters
    ----------
    top_file (str): The filename of the topology.

    Returns
    -------
    angle_indices (list): The indices of all angles.
    dihedral_indices (list): The indices of all dihedrals.
    """
    infile = open(top_file, 'r')
    lines = infile.readlines()
    infile.close()

    n = -1    # line indices (=line number -1)
    angle_start, dihedral_start = False, False 
    angle_indices, dihedral_indices = [], []
    for line in lines:
        n += 1
        if '[ angles ]' in line:
            angle_start = True
        if '[ dihedrals ]' in line:
            dihedral_start = True 
        
        if angle_start is True and line[0] != ';' and line[0] != '[':
            if len(line.split()) == 0:
                angle_start = False 
            else:
                angle_line = line.split()[:3]
                angle_indices.append([int(i) for i in angle_line])

        if dihedral_start is True and line[0] != ';' and line[0] != '[':
            if len(line.split()) == 0:
                dihedral_start = False
            else:
                dihedral_line = line.split()[:4]
                # Note that atom indices might be repeptitive for different dihedrals
                if [int(i) for i in dihedral_line] not in dihedral_indices:
                    dihedral_indices.append([int(i) for i in dihedral_line])

    return angle_indices, dihedral_indices

def write_plumed_input(indices, output_file):
    """ 
    Writes the PLUMED input file for running the plumed driver. 

    Parameters
    ----------
    indices (list): A list of indices of a certain angle/dihedral.
    output_file (str): The file name of the output of plumed driver.
    """
    str1 = ','.join([str(i) for i in indices])

    if len(indices) == 3:   # angle atom indices
        plumed_input = open('plumed_angle.dat', 'w')
        plumed_input.write(f'theta: ANGLE ATOMS={str1}\n')
        plumed_input.write(f'PRINT ARG=theta STRIDE=10 FILE=angle/{output_file}')
        plumed_input.close()

    elif len(indices) == 4: # dihedral atom indices
        plumed_input = open('plumed_dihedral.dat', 'w')
        plumed_input.write(f'theta: TORSION ATOMS={str1}\n')
        plumed_input.write(f'PRINT ARG=theta STRIDE=10 FILE=dihedral/{output_file}')
        plumed_input.close()

def run_plumed_driver(idx_list, trajs):
    """
    Runs the plumed driver to calculate a CV as a function given trajectories of interest.

    Parameters
    ----------
    idx_list (list): A list of indices of all angles/dihedrals
    trajs (str): A list of trajectories filenames as the input to the plumed driver.
    """
    if len(idx_list[0]) == 3:
        a_type = 'angle'  # angle type
    elif len(idx_list[0]) == 4:
        a_type = 'dihedral'

    for i in range(len(idx_list)):
        output_str = '_'.join([str(i) for i in idx_list[i]])
        for j in trajs:
            if 'dihedral_min_1' in j:
                suffix = 'stateA'
            elif 'dihedral_min_2' in j:
                suffix = 'stateB'
            output = f'sys2_{a_type}_{output_str}_{suffix}.dat'
            write_plumed_input(idx_list[i], output)
            os.system(f'plumed driver --mf_xtc {j} --plumed plumed_{a_type}.dat --timestep 2')
            
def plot_distribution(data_file):
    """
    Plots the angle or dihedral distribution given a PLUMED output file.

    Parameters
    ----------
    data_file (str): The filename of the output of fthe plumed driver.
    """
    if 'stateA' in data_file:
        l_type = 'state A'
    elif 'stateB' in data_file:
        l_type = 'state B'    
    
    f = open(data_file, 'r')
    lines = f.readlines()
    f.close()

    theta = []
    for l in lines:
        if l[0] != '#':
            theta.append(float(l.split()[1]))
    theta = np.array(theta) * 180 / np.pi

    plt.hist(theta, bins=100, density=True, alpha=0.5, label=l_type) 

def get_fig_dimension(n_subplots):
    """
    Gets the dimension of the figure given the number of subplots. The figure
    will be as close as to a square as possible.

    Parameters
    ----------
    n_subplots (int): The number of subplots.

    Returns
    -------
    n_rows (int): The number of rows in the figure.
    n_cols (int): The number of columns in the figure.
    """
    if int(np.sqrt(n_subplots) + 0.5) ** 2 == n_subplots:
        # perfect square number
        n_cols = int(np.sqrt(n_subplots))
    else:
        n_cols = int(np.floor(np.sqrt(n_subplots))) + 1 
    
    if n_subplots % n_cols == 0:
        n_rows = int(n_subplots / n_cols)
    else:
        n_rows = int(np.floor(n_subplots / n_cols)) + 1 
    
    return n_cols, n_rows

def plot_all_distributions(data_dir, fig_name):
    files = glob.glob(f'{data_dir}/*')
    files = natsort.natsorted(files)  # [angle1_after,  angle1_before, ...]
    a_type = files[0].split('_')[1]   # angle type
    a_str = a_type[0].upper() + a_type[1:]
    x_label = a_str + ' (deg)'
    n_subplots = int(len(files) / 2)
    n_cols, n_rows = get_fig_dimension(n_subplots)

    fig = plt.figure(figsize=(12, 8))
    for i in range(n_subplots):
        f_list = files[2 * i : 2 * (i + 1)]  # f_list[0]: after 125 ns, f_list[1]: after 125 ns
        plt.subplot(n_rows, n_cols, i + 1)
        plot_distribution(f_list[1])  # plot the data before 125 ns first
        plot_distribution(f_list[0])  # after 125 ns

        if a_type == 'angle':
            indices = [int(i) for i in f_list[0].split('_')[2:5]]
        elif a_type == 'dihedral':
            indices = [int(i) for i in f_list[0].split('_')[2:6]]
        idx_str = '-'.join([str(i) for i in indices])

        plt.xlabel(x_label, fontsize=8)
        plt.ylabel('P.D.F.', fontsize=8)
        plt.xticks(fontsize= 6)
        plt.yticks(fontsize= 6)
        plt.title(f'{a_str} {idx_str}', fontsize=8, weight='bold')

        plt.grid()
        plt.legend(prop={'size': 4})
    
    plt.suptitle(f'The {a_type} distributions of simulations starting from different states', fontsize=12, weight='bold')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(fig_name, dpi=600)


if __name__ == '__main__':
    t1 = time.time()
    trajs = ['../../dihedral_min_1/EXE/Fixed/sys2.xtc', '../../dihedral_min_2/EXE/Fixed/sys2.xtc']
    top = '../../dihedral_min_1/EXE/Fixed/sys2.top'

    args = initialize()
    if args.rerun is True:
        try:
            os.system('rm -r angle')
            os.system('rm -r dihedral')
        except:
            pass 
        os.makedirs('angle')
        os.makedirs('dihedral')

        angle, dihedral = get_atom_indices(top)
        run_plumed_driver(angle, trajs)
        run_plumed_driver(dihedral, trajs)
    
    # Plot the figures!
    rc('font', **{
       'family': 'sans-serif',
       'sans-serif': ['DejaVu Sans'],
       'size': 10
    })
    # Set the font used for MathJax - more on this later
    rc('mathtext', **{'default': 'regular'})
    plt.rc('font', family='serif')

    plot_all_distributions('angle', 'Sys2_remodified_EXE_angle_distributions.png')
    plot_all_distributions('dihedral', 'Sys2_remodified_EXE_dihedral_distributions.png')

    t2 = time.time()
    print(f'Elapsed time: {t2 - t1: 2f} seconds.')
    

