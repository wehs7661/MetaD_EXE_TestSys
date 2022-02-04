import physical_validation

if __name__ == "__main__":
    parser = physical_validation.data.GromacsParser()
    res = parser.get_simulation_data(
        mdp='../mdout.mdp',
        top='../sys2_cccc.top',
        gro='../sys2_cccc_md.gro',
        edr='../sys2_cccc.edr')
    simulation_data = physical_validation.data.SimulationData(
        units=physical_validation.data.UnitData.units("GROMACS"),
        system=res.system,
        ensemble=res.ensemble,
        trajectory=res.trajectory
    )
    physical_validation.kinetic_energy.equipartition(
        data=simulation_data, strict=True, screen=False
    )
