import plumed 
import numpy as np
import matplotlib.pyplot as plt

def analyze(traj, n_blocks, discard=0):
    """
    This function returns average and error with bootstrap
    
    Parameters
    ----------
    traj (pandas.DataFrame): trajectory data (content of COLVAR)
    nblocks (int): number of blocks
    discard (float): discarded fraction
    """
    n = int(len(traj) * (1.0 - discard))   # number of data points considered
    # make sure the number of frames is a multiple of nblocks (discard the first few frames)
    n = (n // n_blocks) * n_blocks
    bias = np.array(traj["metad.bias"])
    bias -= np.max(bias) # avoid overflows
    w = np.exp(bias / kBT)[-n:].reshape((n_blocks, -1)) # shape: (nblocks, nframes in one block), weight for each point
    
    # A: coupled state, B: uncoupled state
    isA = np.int_(traj["lambda"] == 0)[-n:].reshape((n_blocks, -1)) # 1 if in A (np.in_ converts bool to 0 or 1)
    isB = np.int_(traj["lambda"] == np.max(traj["lambda"]))[-n:].reshape((n_blocks, -1)) # 1 if in B
    
    B = 200 # number of bootstrap iterations
    boot = np.random.choice(n_blocks, size=(B, n_blocks))  # draw samples from np.arange(n_blocks), size refers the output size
    popA = np.average(isA[boot], axis=(1,2), weights=w[boot])  # Note that isA[boot] is a 3D array
    popB = np.average(isB[boot], axis=(1,2), weights=w[boot])  # shapes of popA and popB: (B,)

    df = np.log(popA / popB) # this is in kBT units
    popA0 = np.average(isA, weights=w)
    popB0 = np.average(isB, weights=w)
    return np.log(popA0 / popB0), np.std(df)

if __name__ == "__main__":

    np.random.seed(0)
    kBT = 2.4777090399459767

    colvar_rew = plumed.read_as_pandas('COLVAR_SUM_BIAS')
    
    # block analysis
    dd = []
    nblocks = [2000, 1000, 500, 200, 50, 20]
    for nb in nblocks:
        dd.append(analyze(colvar_rew, nb, discard=0.0))
    dd=np.array(dd)
    print(dd)   # free energy difference and its uncertainty given different block sizes

    plt.plot(len(colvar_rew) / np.array(nblocks), dd[:,1], "x-")
    plt.xscale("log")
    plt.title("Block analysis from full trajectory")
    plt.xlabel("block size (# frames)")
    plt.ylabel("error")
    plt.savefig('fes.png', dpi=600)
