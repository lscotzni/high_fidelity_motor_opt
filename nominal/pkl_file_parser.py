import pickle

file_name = '_case_archive/2022-11-03-10_51_18/_data/data_entry.simulator.2022-11-05-18_55_29_805104.pkl'

# with open('data_entry.simulator.2022-08-14-01_17_32_023440_Nom.pkl', 'rb') as f:
#     data = pickle.load(f)

with open(file_name, 'rb') as f:
    data = pickle.load(f)
