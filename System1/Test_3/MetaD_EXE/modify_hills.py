from free_energy_estimator import FreeEnergy_HILLS

for i in range(1, 21):
    estimator = FreeEnergy_HILLS(f'rep_{i}/HILLS_LAMBDA')
    estimator.deltaF_average(3000, 5000)   # generate modified HILLS file for all reps



