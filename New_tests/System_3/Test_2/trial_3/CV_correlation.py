import time
import plumed 
import argparse
import matplotlib.pyplot as plt
from matplotlib import rc

def initialize():
    parser = argparse.ArgumentParser(
        description='This code plots the distribution of a CV for different lambda states \
                     to show how the lambda variable correlates with the CV.')
    parser.add_argument('-i',
                        '--input',
                        help='The PLUMED output file as the input.')
    parser.add_argument('-c',
                        '--CV',
                        help='The name of CV in the input file.')
    parser.add_argument('-n',
                        '--n_lambda',
                        type=int,
                        default=40,
                        help='The number of lambda states.')
    parser.add_argument('-nb',
                        '--nbins',
                        type=int,
                        default=200,
                        help='The number of bins for the histograms.')
    parser.add_argument('-x',
                        '--xlabel',
                        help='The variable name of the x-axis.')
    parser.add_argument('-t',
                        '--title',
                        help='The supbtitle of the figure.')

    args_parse = parser.parse_args()

    return args_parse


if __name__ == "__main__":
    t1 = time.time()

    rc('font', **{
       'family': 'sans-serif',
       'sans-serif': ['DejaVu Sans'],
       'size': 10
       })
    # Set the font used for MathJax - more on this later
    rc('mathtext', **{'default': 'regular'})
    plt.rc('font', family='serif')

    args = initialize()

    data = plumed.read_as_pandas(args.input)

    n_rows, n_cols = 5, 8   # should change with args.n_lambda but I'm lazy ...
    _, ax = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(16, 10))  
    for i in range(args.n_lambda): 
        plt.subplot(5, 8, i + 1)   
        hist = plt.hist(data[data['lambda'] == i][args.CV], bins=args.nbins, label=f'$\lambda$={i + 1}')
        if (i + 1) % n_cols == 1:
            plt.ylabel('Count')     
        if (i + 1) > (n_rows - 1) * n_cols:
            plt.xlabel(args.xlabel)
        plt.grid()
        plt.title(f'$\lambda$={i}')
    plt.suptitle(args.title, fontsize=16, weight='bold')
    plt.tight_layout()
    plt.savefig(f'all_lambda_{args.CV}.png', dpi=600)
    
    print(f'Elapsed time: {time.time() - t1:.0f} s.')
