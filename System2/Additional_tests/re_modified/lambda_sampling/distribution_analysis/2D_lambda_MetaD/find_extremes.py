import glob
import natsort
import numpy as np 

if __name__ == "__main__":
    all_files = glob.glob('*.dat')
    files = natsort.natsorted(all_files, reverse=False)
    
    for f in files:
        data = np.transpose(np.loadtxt(f))
        t, theta = data[0], data[1] * 180 / np.pi
        angle = '-'.join(f.split('_state')[0].split('angle_')[1].split('_'))
        print(f'Analyzed file: {f}')
        print(f'--> Angle {angle}: Max: {np.max(theta)} degrees, Min: {np.min(theta)} degrees\n')


