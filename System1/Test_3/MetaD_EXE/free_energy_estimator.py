import os
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

    def deltaF_average(self, t_0, t_f=None, sample_cmd=None):
        """
        This function averages the free energy difference between the last and the 
        first state (diff = last - first) over a last certain portion of the simulation
        by analyzing a HILLS file. Suitable for alchemical metadynamics. 

        Parameters
            t_0          (float): the "window time" in ps. For example, t_0 = 4000 if
            we want to average delta_F over the last ns in a 5 ns simulation.
            t_f          (float): the simulation length to be considered
            sample_cmd   (str): the PLUMED sum_hills command without the flag specifying
            the name of the input HILLS file. If the value is not given, no sum_hills command
            will be run and only the modified HILLS file will be generated.
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

        if t_f is None:
            t_f = np.transpose(np.loadtxt(self.hills))[0][-1]

        # data[0] = time, data[-2] = height
        data = np.transpose(np.loadtxt(self.hills))
        
        # slice the data if needed
        data_sliced = []
        for i in range(len(data)):
            data_sliced.append(data[i][data[0] <= t_f])
        data_sliced = np.array(data_sliced)

        for i in range(len(data_sliced[-2])):
            if data_sliced[0][i] > t_0:  # t_0 in ps
                data_sliced[-2][i] *= (t_f - data_sliced[0][i]) / (t_f - t_0)

        np.savetxt(self.hills + "_modified", np.transpose(data_sliced), header=metatext[:-1], comments='#! ', delimiter='    ')

        if sample_cmd is not None:
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
        t_f = np.transpose(np.loadtxt(self.hills))[0][-1]
        n_files = int(t_f / stride) + 1
        os.system(sample_cmd + f' --stride {stride_G}')
        fes, delta_F = [], []
        kT = 1   # so the units of delta_F are kT
        for i in range(n_files):
            fes.append(np.loadtxt("fes_" + str(i) + ".dat"))
        
        for i in range(len(fes)):
            if fes[i].shape[1] == 2:
                # 1D metaD or projection of multi-dimentional MetaD
                # fes[i].columns[1] returns the name of the second column
                delta_F.append(fes[i][-1][1] - fes[i][0][1])

            else:
                # parse the input file
                f = open('fes_0.dat', 'r')
                lines = f.readlines()
                f.close()

                for l in lines:
                    if 'FIELDS' in l:
                        col_names = l.split('#! FIELDS')[1].split() 
                        col_idx = -1
                        for col in col_names:
                            col_idx += 1
                            if col == 'lambda':
                                lambda_idx = col_idx
                            if col == 'file.free':
                                fes_idx = col_idx
                        break
                
                N_states = max([fes[i][j][lambda_idx] for j in range(len(fes[i]))])
                lambda_final = np.array([fes[i][j][fes_idx] for j in range(len(fes[i])) if fes[i][j][lambda_idx] == N_states])
                lambda_start = np.array([fes[i][j][fes_idx] for j in range(len(fes[i])) if fes[i][j][lambda_idx] == 0])
                
                delta_F.append(
                        kT * np.log(np.sum(np.exp(lambda_final / kT)) /                                    np.sum(np.exp(lambda_start / kT)))
                        )
                
        os.system('rm fes_*')
        return delta_F

# class FreeEnergy_alchemlyb 



