import physical_validation
import numpy as np
import time

if __name__ == "__main__":
    t1 = time.time()
    parser = physical_validation.data.GromacsParser()

    res = parser.get_simulation_data(
    mdp='../mdout.mdp',
    top='sys2_cccc_lig.top',
    edr='../sys2_cccc.edr',
    trr='sys2_cccc_lig.trr'
    )

    res.system.ndof_reduction_tra = 0

    results = physical_validation.kinetic_energy.equipartition(
        data=res,
        strict=False,
        filename='2d_lambda',
    )

    print(results)

    t2 = time.time()
    print(f'Time elapsed: {t2-t1} seconds.')
