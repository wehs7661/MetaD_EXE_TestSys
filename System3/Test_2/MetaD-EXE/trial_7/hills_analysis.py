import numpy as np
from free_energy_estimator import FreeEnergy_HILLS

sample_cmd = 'plumed sum_hills --idw lambda --min 0,0 --max 39,50 --bin 39,200 --outfile fes_test --kt 2.4777090399459767'

df = []
estimator = FreeEnergy_HILLS(f'HILLS_2D')
df.append(estimator.deltaF_average(sample_cmd, 18000, 20000) / 2.4777090399459767)

print(df)
#print(np.mean(df))
#print(np.std(df))


