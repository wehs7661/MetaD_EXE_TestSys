import argparse
import numpy as np 
import os 

# Note: this script is able to complete the following tasks for a 2D lambda-metadynamics
# 1. Generate fes.dat if it is not provided.
# 2. Plot the free energy as a function of alchemical states if needed
# 3. Output the weights in alchemical space for expanded ensemble

def initialize(args):
    parser = argparse.ArgumentParser(
        description='This code performs data analysis for 2D lambda-metadynamics.')
    parser.add_argument('-f'
                        '--fes'
                        help='The file containing the data of ')








