import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc


if __name__ == "__main__":
    data = np.transpose(np.loadtxt('COLVAR'))
    t1, t2 = data[0][:500001], data[0][500001:][::10]
    theta_1, theta_2 = data[1][:500001], data[1][500001:][::10]
    lambda_1, lambda_2 = data[2][:500001], data[2][500001:][::10]

    plt.figure()
    plt.subplot(1, 2, 1)
    plt.hist(theta_1, bins=100)
    plt.subplot(1, 2, 2)
    plt.hist(theta_2, bins=100)
    plt.savefig('test.png')

    plt.figure()
    plt.subplot(1, 2, 1)
    plt.hist(lambda_1, bins=20)
    plt.subplot(1, 2, 2)
    plt.hist(lambda_2, bins=20)
    plt.savefig('lambda_distribution.png', dpi=600)

