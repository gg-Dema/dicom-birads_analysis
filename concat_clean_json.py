import pandas as pd
import os

path_birads_file=r"dataset/clean_json"
print(path_birads_file)
birads_file = os.listdir(path_birads_file)
dtype = 'str'

file1 = pd.read_csv(os.path.join(path_birads_file, birads_file[0]), sep=';', dtype=dtype)
file3 = pd.read_csv(os.path.join(path_birads_file, birads_file[1]), sep=';', dtype=dtype)
file4 = pd.read_csv(os.path.join(path_birads_file, birads_file[2]), sep=';', dtype=dtype)
file = pd.concat([file1, file3, file4], ignore_index=True)

file.to_csv(os.path.join('dataset', 'file_JsonBirads_sum.csv'), sep=';', index=False )
