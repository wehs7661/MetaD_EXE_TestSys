import numpy as np
from free_energy_estimator import FreeEnergy_HILLS

sample_cmd = 'plumed sum_hills --min 0 --max 8 --bin 8 --outfile fes_test'

df = []
estimator = FreeEnergy_HILLS(f'HILLS_LAMBDA')
df.append(estimator.deltaF_average(sample_cmd, 4000, 5000)/2.4777090399459767)

print(df)
print(np.mean(df))
print(np.std(df))


