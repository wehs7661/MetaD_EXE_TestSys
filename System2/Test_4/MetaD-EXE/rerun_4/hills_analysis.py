import numpy as np
from free_energy_estimator import FreeEnergy_HILLS

sample_cmd = 'plumed sum_hills --idw lambda --min -pi,0 --max pi,8 --bin 50,8 --outfile fes_test --kt 2.4777090399459767'

df = []
for i in range(1, 4):
    estimator = FreeEnergy_HILLS(f'rep_{i}/HILLS_2D')
    df.append(estimator.deltaF_average(18000, sample_cmd) / 2.4777090399459767)

print(df)
print(np.mean(df))
print(np.std(df))


