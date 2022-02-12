import numpy as np

def extract_data(input_f, n_cols, freq=1):
    """
    This function extract data from an xvg or a dat file given the file name and the column number(s).

    Parameters
    ----------
    input_f : str
        The input file.
    freq: int
        The frequency (units: line) to extract the data
    n_cols : array-like
        The column number of interest (starting from 1).

    Returns
    -------
    data : np.array
        The extracted data    
    """
    
    f = open(input_f, 'r')
    lines = f.readlines()
    f.close()

    data, all_data = [], []
    for i in range(len(n_cols)):
        all_data.append([])
        data.append([])

    for l in lines:
        if l[0] != '#' and l[0] != '@':
            for i in range(len(n_cols)):
                all_data[i].append(float(l.split()[n_cols[i] - 1]))

    for j in range(len(n_cols)):
        data[j] = np.array([all_data[j][i] for i in range(len(all_data[j])) if i % freq == 0])

    return data


if __name__ == '__main__':
    state_data = extract_data('sys2.dhdl.xvg', [1, 2], 10)
    theta_data = extract_data('dihedral_min_1.dat', [1, 2], 1)
    t1, state = state_data[0] / 1000, state_data[1]
    t2, theta = theta_data[0], theta_data[1] * (180 / np.pi)

    # Now t1 and t2 should be the same and let's discard the all the data where lamdba is not 0 
    t, theta_0 = [], []
    for i in range(len(state)):
        if state[i] == 0:
            t.append(t1[i])
            theta_0.append(theta[i])
    
    print(f'At lambda=0, the largest and smallest dihedral angles are {np.max(theta_0): .3f} (t = {t[theta_0.index(max(theta_0))]} ns) and {np.min(theta_0): .3f} (t = {t[theta_0.index(min(theta_0))]} ns), respectively.')
