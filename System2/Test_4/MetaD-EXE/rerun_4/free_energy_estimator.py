import os
import plumed 
import numpy as np

class FreeEnergy_HILLS:
    """A class for free energy claculations by analyzing a PLUMED HILLS file."""
    def __init__(self, hills_file):
        """
        This function initializes the class FreeEnergy_HILLS

        Parameters
            hills_file  (str): the file name of the PLUMED HILLS file.

        Attributes
            hills       (str): the file name of the PLUMED HILLS file
            t_f         (float): the simulation length in ps
        """
        self.hills = hills_file
        self.t_f = np.transpose(np.loadtxt(hills_file))[0][-1]

    def deltaF_average(self, t_0, sample_cmd):
        """
        This function averages the free energy difference between the last and the 
        first state (diff = last - first) over a last certain portion of the simulation
        by analyzing a HILLS file. Suitable for alchemical metadynamics. 

        Parameters
            t_0          (float): the "window time" in ps. For example, t_0 = 4000 if 
            we want to average delta_F over the last ns in a 5 ns simulation.
            sample_cmd   (str): the PLUMED sum_hills command without the flag specifying
            the name of the input HILLS file.

        Returns
            delta_F      (float): the free energy difference between the coupled and 
            uncoupled states averaged over the last t_f - t_0 ps. (units: kT)
        """
        # Modify the HILLS file
        f = open(self.hills, 'r')
        lines = f.readlines()
        f.close()

        metatext = ''
        for l in lines:
            if l[0] == '#':
                metatext += l[3:]  # remove "
            else:
                break

        # data[0] = time, data[-2] = height
        data = np.transpose(np.loadtxt(self.hills))

        for i in range(len(data[-2])):
            if data[0][i] > t_0:  # t_0 in ps
                data[-2][i] *= (self.t_f - data[0][i]) / (self.t_f - t_0)

        np.savetxt(self.hills + "_modified", np.transpose(data), header=metatext[:-1], comments='#! ', delimiter='    ')

        # Sum up the modified hills and get delta_F
        os.system(sample_cmd + f" --hills {self.hills + '_modified'}")
        if '--outfile' in sample_cmd:
            fes_file = sample_cmd.split('--outfile ')[1].split()[0]
        else:
            fes_file = 'fes.dat'
        f = np.transpose(np.loadtxt(fes_file))[1]
        delta_f = f[-1] - f[0]  # free energy difference

        return delta_f

    def deltaF_evolution(self, sample_cmd, pace, stride=10, dt=0.002):
        """
        This function calls sum_hills to get the time series of the free energy
        difference between the coupled and uncoupled states.

        Parameters
            sample_cmd (str): the PLUMED sum_hills command without the flag stride
            pace       (float): the PACE specified in the PLUMED input file
            stride     (float): the stride of outputting a fes file (units: ps)
            dt         (float): dt specifie in the GROMACS .mdp file
        """
        stride_G = int((stride) / (pace * dt))  # stride in the units of Gaussian
        n_files = int(self.t_f / stride) + 1
        os.system(sample_cmd + f' --stride {stride_G}')
        fes, delta_F = [], []
        kT = 1   # so the units of delta_F are kT
        for i in range(n_files):
            fes.append(plumed.read_as_pandas("fes_" + str(i) + ".dat"))
        
        N_states = max(fes[0]['lambda'])
        for i in range(len(fes)):
            if fes[i].shape[1] == 2:
                # 1D metaD or projection of multi-dimentional MetaD
                # fes[i].columns[1] returns the name of the second column
                delta_F.append(fes[i][fes[i].columns[1]].iloc[-1] - fes[i][fes[i].columns[1]].iloc[0])

            else:
                delta_F.append(
                    kT * np.log(np.sum(np.exp(fes[i].loc[fes[i]['lambda'] == N_states]["file.free"] / kT)) /
                                np.sum(np.exp(fes[i].loc[fes[i]['lambda'] == 0.0]["file.free"] / kT)))
                )   
        
        os.system('rm fes_*')
        return delta_F

# class FreeEnergy_alchemlyb 



