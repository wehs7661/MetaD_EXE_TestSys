import parmed
from simtk.openmm.app import PDBFile
from openforcefield.topology import Molecule, Topology
from openforcefield.typing.engines.smirnoff import ForceField

LAC = Molecule.from_smiles("C[C@@H](O)C(O)=O")

# Obtain the OpenMM Topology object from the PDB file.
pdbfile = PDBFile('sys2_init.pdb')
omm_topology = pdbfile.topology

# Create the Open Forcefield Topology.
off_topology = Topology.from_openmm(omm_topology, unique_molecules=[LAC])

# Load the "Parsley" force field.
forcefield = ForceField('openff_unconstrained-1.0.0.offxml')
omm_system = forcefield.create_openmm_system(off_topology)

# convert OpenMM System to a ParmEd structure.
parmed_structure = parmed.openmm.load_topology(omm_topology, omm_system, pdbfile.positions)

# Export GROMACS files.
parmed_structure.save('system.top', overwrite=True)
parmed_structure.save('system.gro', overwrite=True)
