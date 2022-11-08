import plumed 


if __name__ == "__main__":
    data = plumed.read_as_pandas('HILLS')
    data_1D = data[data['a'].isna()].reset_index(drop=True)
    data_2D = data[~data['a'].isna()].reset_index(drop=True)
    
    data_1D = data_1D.drop(columns=['a', 'b'])
    data_2D.columns = ['time', 'lambda', 'n', 'sigma_lambda', 'sigma_n', 'height', 'biasf']

    plumed.write_pandas(data_1D, 'HILLS_1')
    plumed.write_pandas(data_2D, 'HILLS_2')
