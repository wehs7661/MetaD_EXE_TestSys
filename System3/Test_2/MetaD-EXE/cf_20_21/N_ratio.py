import copy 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc 

if __name__ == '__main__':
    # Plot the figures!
    rc('font', **{
       'family': 'sans-serif',
       'sans-serif': ['DejaVu Sans'],
       'size': 10
    })
    # Set the font used for MathJax - more on this later
    rc('mathtext', **{'default': 'regular'})
    plt.rc('font', family='serif')

    CV_idx = [1, 2]
    bins = [200, 40]
    CVs = ['water', 'lambda']
    names = ['configurational CV', '$ \lambda $']
    for cv in CV_idx:
        plt.figure()
        for i in [20, 21]:
            data = np.transpose(np.loadtxt(f'COLVAR_trial_{i}'))
            time = data[0]
            if i == 21:
                time = time[time <= 20000]
            CV_data = data[cv]
            CV_data = CV_data[:len(time)]
            
            l_t = len(time)
            time_original = copy.deepcopy(time)
            CV_original = copy.deepcopy(CV_data)
            t, N_ratio = [], []
            
            for j in np.arange(11, 101, 1):
                time = time_original[:int(0.01 * j * l_t)]
                CV_data = CV_original[:int(0.01 * j * l_t)]
                if cv == 1:
                    CV_data = CV_data[CV_data < 12]
                    CV_data = CV_data[CV_data > 1]
                hist = np.histogram(CV_data, bins=bins[cv - 1])[0]
                #hist = hist[hist != 0]
                t.append(time[-1])
                N_ratio.append(np.max(hist) / np.min(hist))
            plt.plot(t, N_ratio, label=f'Trial {i}')
        
        #plt.ylim([0, 12])
        #if cv == 1:
        #    plt.hlines(1, 2000, 20000, linestyle='--')
        plt.xlabel('Time (ps)')
        plt.ylabel(f'N ratio ({names[cv -1]} direction)')
        plt.grid()
        plt.legend()
        plt.savefig(f'N_ratio_{CVs[cv -1]}.png', dpi=600)

