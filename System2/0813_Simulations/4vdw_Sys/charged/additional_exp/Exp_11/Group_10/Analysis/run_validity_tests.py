import os
import glob
import physical_validation
import numpy as np
import time
import pickle
import contextlib

if __name__ == "__main__":
    t1 = time.time()
    
    p_values, z_scores = [], []
    bools = [True, False]
    test_type = ['strict', 'non-strict']
    times = np.linspace(0, 60000, 7)

    trr_files = glob.glob('*.trr')
    if len(trr_files) < 6:
        for i in range(6):
            os.system(f'echo 2 | gmx trjconv -s ../sys2_cccc.tpr -f ../sys2_cccc.trr -o sys2_cccc_lig_{i}.trr -b {times[i]} -e {times[i + 1]}')

    for i in range(len(bools)):
        for j in range(6):
            print(f'Running {test_type[i]} tests for the trajectory from {times[j]} to {times[j + 1]} ps ...')

            parser = physical_validation.data.GromacsParser()

            res = parser.get_simulation_data(
            mdp='../mdout.mdp',
            top='sys2_cccc_lig.top',
            edr='../sys2_cccc.edr',
            trr=f'sys2_cccc_lig_{j}.trr'
            )

            res.system.ndof_reduction_tra = 0
            with open(f'results_{test_type[i]}_{j}.txt', 'w') as f:
                with contextlib.redirect_stdout(f):
                    results = physical_validation.kinetic_energy.equipartition(
                        data=res,
                        strict=bools[i],
                        filename=f'exp11_group10_{int(times[j])}_{int(times[j + 1])}',
                    )
                    f.write(str(results))

    t2 = time.time()
    print(f'Time elapsed: {t2-t1} seconds.')
