import numpy as np
import argparse
import matplotlib.pyplot as plt
from pymbar import timeseries
from matplotlib import rc 

def initialize():
    parser = argparse.ArgumentParser(
        description='This code plots a time series and prints out the results by pymbar.timeseries.')
    parser.add_argument('-i',
                        '--input',
                        help='The file name containing the time series.')
    parser.add_argument('-n',
                        '--nskip',
                        type=int,
                        default=100,
                        help='The value of the nskip parameter used in timeseries module.')
    args_parse = parser.parse_args()

    return args_parse


if __name__ == '__main__':
    rc('font', **{
       'family': 'sans-serif',
       'sans-serif': ['DejaVu Sans'],
       'size': 10
       })
    # Set the font used for MathJax - more on this later
    rc('mathtext', **{'default': 'regular'})
    plt.rc('font', family='serif')

    args = initialize()
    data = np.transpose(np.loadtxt(args.input))
    time, n = data[0] / 1000, data[1]  # units of time: ns
    
    rc('font', **{
       'family': 'sans-serif',
       'sans-serif': ['DejaVu Sans'],
       'size': 10
    })
    # Set the font used for MathJax - more on this later
    rc('mathtext', **{'default': 'regular'})
    plt.rc('font', family='serif')
    
    plt.figure()
    plt.plot(time, n)
    plt.xlabel('Time (ns)')
    plt.ylabel('$ \lambda $')
    plt.grid()
    plt.savefig('sys3_1D_lambda_water_0.35.png')

    print(f'mean: {np.mean(n)}')
    print(f'max: {np.max(n)}')
    print(f'min: {np.min(n)}')

    dt = time[1] - time[0]
    [t, g, N_eff] = timeseries.detectEquilibration(n, nskip=args.nskip)
    print(f'dt: {dt} ns')
    print(f't0 = {t * dt: .3f} ns')
    print(f'g = {g: .3f}')
    print(f'Correlation time: {(g - 1) / 2 * dt: .3f} ns')
    print(f'N_eff = {N_eff: .3f}')
    


    



