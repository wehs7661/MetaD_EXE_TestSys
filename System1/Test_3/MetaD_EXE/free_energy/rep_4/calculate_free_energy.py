import os 
import glob
import natsort 
import argparse 
import numpy as np 
import matplotlib.pyplot as plt 
from matplotlib import rc 

def initialize():
    parser = argparse.ArgumentParser(
        description='This code calculates the free energy profile and assess \
                    the influence of the block size on its uncertainty.')
    parser.add_argument('-i',
                        '--input',
                        default='plumed_reweight.dat',
                        help='The PLUMED input file for reweighting.')
    parser.add_argument('-b',
                        '--b_sizes',
                        nargs='+',
                        type=float,
                        help='The min, max and the spacing of the block sizes, in the units of \
                              the STRIDE used to print COLVAR in metadynamics. For example, if \
                              the this argument is set to 5000 and STRIDE=10 was used in the PLUMED\
                              input file for running the metadynamics, then the real block size is \
                              50000 simulation steps. If dt = 0.002 ps, this means 100 ps. For this\
                              argument, if only one value is given, only one free energy profile based \
                              on the given value will be calcualted. (Only one fes_*.dat file.)')
    parser.add_argument('-n',
                        '--n_CVs',
                        default=1,
                        help='The number of CVs.')
    parser.add_argument('-f',
                        '--factor',
                        type=float,
                        default=0.02,
                        help='The factor for converting the block size into ps.')
    parser.add_argument('-t',
                        '--truncation',
                        type=float,
                        default=0.8,
                        help='The truncation fraction.')
    args_parse = parser.parse_args()

    return args_parse 

def logger(file_name='free_energy_results.txt', *args, **kwargs):
    print(*args, **kwargs)
    with open(file_name, "a") as f:
        print(file=f, *args, **kwargs)

def clear_directory(file_name):
    if type(file_name) == str:
        if os.path.isfile(file_name):
            os.remove(file_name)
    elif type(file_name) == list:
        for i in file_name:
            clear_directory(i)

def prepare_plumed_input(template, b_size):
    f = open(template, 'r')
    lines = f.readlines()
    f.close()
    
    line_n = -1  # line number
    for line in lines:
        line_n += 1
        if 'CLEAR' in line:
            lines[line_n] = f'CLEAR={b_size}\n'
        if 'DUMPGRID' in line:
            line_split = line.split('STRIDE=')
            line_split[-1] = f'STRIDE={b_size}\n'
            lines[line_n] = ''.join(line_split)

    output = open(template, 'w')
    output.write(''.join(lines))       
    output.close()

def read_histogram(hist_file):
    data = np.loadtxt(hist_file)
    with open(hist_file, "r") as f:
        for line in f:
            if line.startswith('#! SET normalisation'):
                norm = float(line.split()[-1])
    hist = data[:, -1]  # normalized probability: the last column
    
    return norm, hist

def calculate_free_energy(hist_dir, hist_files):
    # Step 1: Calculate the average of the weighted histogram for each gridded CV value
    w_sum, avg = 0, 0
    for f in hist_files:
        norm, hist = read_histogram(f'{hist_dir}/{f}')
        w_sum += norm
        avg += norm * hist
    avg = avg / w_sum
    
    # Step 2: Calculate the uncertainty of each gridded CV value
    error = 0
    for f in hist_files:
        norm, hist = read = read_histogram(f'{hist_dir}/{f}')
        error += norm * norm * (hist - avg) ** 2
    error = np.sqrt(error / (w_sum **2))
        
    # Step 3: Conver to the uncertainty in free energy 
    fes = -np.log(avg)    # units: kT
    f_err = error / avg   # units: kT
    
    return fes, f_err


if __name__ == '__main__':
    args = initialize()
    
    if len(args.b_sizes) == 1:
        multi_b_size = False
        blocks = [args.b_sizes[0]]
    else:  
        print(args.b_sizes)
        multi_b_size = True
        try:
            os.system('rm -r FES')
        except:
            pass
        os.makedirs('FES')
        blocks = np.arange(args.b_sizes[0], args.b_sizes[1] + args.b_sizes[2], args.b_sizes[2])
    
    rc('font', **{
       'family': 'sans-serif',
       'sans-serif': ['DejaVu Sans'],
       'size': 10
    })
    # Set the font used for MathJax - more on this later
    rc('mathtext', **{'default': 'regular'})
    plt.rc('font', family='serif')

    delta_f_err = []
    for  b_size in blocks:
        # Step 1: Clear directory
        rm_list = ['COLVAR_REWEIGHT', 'weights.dat', glob.glob('bck.*'), glob.glob('fes*'), glob.glob('histograms/*')]
        for i in rm_list:
            clear_directory(i)
        
        # Step 2: Prepare the PLUMED input file
        prepare_plumed_input(args.input, b_size)

        # Step 3: Run plumed driver to get weighted histograms
        os.system(f'plumed driver --plumed {args.input} --noatoms')

        # Step 4: Free energy calculations 
        files = []
        for f in os.listdir('histograms'):
            if f.endswith('hist.dat'):
                files.append(f)
        files = natsort.natsorted(files, reverse=False)
        fes, f_err = calculate_free_energy('histograms', files)
        
        CV_points = []
        for i in range(args.n_CVs):
            CV_points.append(np.transpose(np.loadtxt('histograms/hist.dat'))[i])  # time series of the i-th CV
        
        if multi_b_size is False:   # only one fes_*.dat
            fes_file = open(f'fes_bsize_{b_size}.dat', 'w')
        else:
            fes_file = open(f'FES/fes_bsize_{b_size}.dat', 'w')
        for i in range(len(CV_points[0])):
            CV_str = ''
            for j in range(args.n_CVs):
                CV_str += f'{CV_points[j][i]: .3f}'  # the value of the j-th dimension of 
                fes_file.write(f'{CV_str}    {fes[i]: .6f}    {f_err[i]: .6f}\n')

        delta_f_err.append(np.sqrt(f_err[-1] ** 2 + f_err[0] ** 2))
        if multi_b_size:
            logger('FES/free_energy_results.txt', f'The free energy difference is {fes[-1]-fes[0]: .6f} +/- {delta_f_err[-1]: .6f} kT. (Block size: {b_size} steps, or {b_size * args.factor} ps.)')
        else:
            print(f'The free energy difference is {fes[-1]-fes[0]: .6f} +/- {delta_f_err[-1]: .6f} kT. (Block size: {b_size} steps, or {b_size * args.factor} ps.)')

    if multi_b_size:
        plt.figure()
        plt.plot(blocks * args.factor, delta_f_err)
        plt.xlabel('Block size (ps)')
        plt.ylabel('Uncertainty in the free energy difference ($k_{B}T$)')
        plt.title('The uncertainty as a function of block size')
        plt.grid()
        plt.savefig('FES/delta_f_blocks.png', dpi=600)




