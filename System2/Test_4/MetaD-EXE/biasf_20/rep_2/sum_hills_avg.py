import os 
import numpy as np
from rich.progress import track
import time
#from tqdm.auto import tqdm

def logger(*args, **kwargs):
    print(*args, **kwargs)
    with open("sum_hills_log.txt", "a") as f:
        print(file=f, *args, **kwargs)

def save_data(*args, **kwargs):
    with open("sum_hills_data.txt", "a") as f:
        print(file=f, *args, **kwargs)

if __name__ == '__main__':
    t1 = time.time()
    os.system("rm *txt")
    plumed_cmd = "plumed sum_hills --hills HILLS_2D --idw lambda --kt 2.4777090399459767 --min -3.141592653589793,0.0000 --max 3.141592653589793,8.0000 --spacing 0.01,0.01 --stride "

    start = 200000   # 200000 Gaussians, 2000000 steps, 4 ns
    step = 100       # output a file for every 100 Gaussians (2 ps, same as nstlog)

    logger("Start executing sum_hills functions for HILLS_LAMBDA ...\n")
    save_data("# Free energy difference as a function of time")
    save_data(f"# Base command: {plumed_cmd}" + "NUM_STRIDE")
    save_data("# Column 1: Time (ps); Column 2: Free energy difference (kT)")
    
    for i in track(range(501)):    # 100 * 500 = 50000 Gaussians, 1 ns
        t = (start + step * i) * 0.02
        cmd = plumed_cmd + str(int(start + step * i))
        logger(f"Executing the command {cmd} ...")
        os.system(cmd)
        
        fes = np.loadtxt("fes_0.dat")
        diff = fes[-1][1] - fes[0][1]   # free energy difference
        save_data(f"{t}" + "   " + f"{diff}")
        os.system("rm fes_*")

    logger("Reading sum_hills_data.txt")    
    data = np.loadtxt("sum_hills_data.txt")
    fes_series = np.array([data[i][1] for i in range(501)])
    logger(f"Free energy difference averaging over tha last 1 ns: {np.mean(fes_series)}")
    t2 = time.time()
    logger(f"Time elapsed: {t2 - t1} ")






