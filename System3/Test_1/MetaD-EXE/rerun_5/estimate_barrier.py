import numpy as np
import argparse

def initialize():
    parser = argparse.ArgumentParser(
        description='This code estimate the energy barrier.')
    parser.add_argument('-f', 
                        '--file',
                        type=str,
                        help='The file name of the fes.dat file.')
    args_parse = parser.parse_args()

    return args_parse

if __name__ == '__main__':





