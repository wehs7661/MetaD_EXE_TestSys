import argparse
import numpy as np 

def initialize():
    parser = argparse.ArgumentParser(
        description='This code plots the angle and dihedral angle distribution for the modified System 2.')
    parser.add_argument('-c',
                        '--cutoff',
                        type=float,
                        default=12,
                        help='The cutoff of the number of water molecules. Data above this number will not be considered.')
    parser.add_argument('-n',
                        '--num',
                        help='Test number')
    args_parse = parser.parse_args()

    return args_parse

if __name__ == "__main__":
    args = initialize()

    data = np.transpose(np.loadtxt(f'test_{args.num}/COLVAR'))
    n = data[1]
    hist = np.histogram(n, bins=200)[0]
    print(f'Before truncation: N_ratio = {np.max(hist) / np.min(hist)}')
    
    n = n[n < args.cutoff]
    hist = np.histogram(n, bins=200)[0]
    print(f'Cutoff: 12, N_ratio = {np.max(hist) / np.min(hist)}')

