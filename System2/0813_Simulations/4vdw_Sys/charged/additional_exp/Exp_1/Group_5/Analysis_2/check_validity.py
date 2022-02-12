import physical_validation
import numpy as np
import time

if __name__ == "__main__":
    t1 = time.time()
    parser = physical_validation.data.GromacsParser()

    res_1 = parser.get_simulation_data(
    mdp='../mdout.mdp',
    top='sys2_cccc_lig.top',
    edr='../sys2_cccc.edr',
    trr='sys2_cccc_lig_part1.trr'
    )
    res_2 = parser.get_simulation_data(
    mdp='../mdout.mdp',
    top='sys2_cccc_lig.top',
    edr='../sys2_cccc.edr',
    trr='sys2_cccc_lig_part2.trr'
    )

    res_1.system.ndof_reduction_tra = 0
    res_2.system.ndof_reduction_tra = 0

    results_1 = physical_validation.kinetic_energy.equipartition(
        data=res_1, 
        strict=True, 
        filename='2d_lambda_part1',
    )

    print('\n')

    results_2 = physical_validation.kinetic_energy.equipartition(
        data=res_2,
        strict=True,
        filename='2d_lambda_part2',
    )

    print('\nPart 1')
    print(results_1)

    print('\nPart 2')
    print(results_2)

    t2 = time.time()
    print(f'Time elapsed: {t2-t1} seconds.')
