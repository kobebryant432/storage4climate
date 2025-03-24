import xarray as xr
import shutil
import time
import os
import pathlib
import numpy as np

reg_data_dir = 'test_data'                      # your uncompressed data dir
compr_data_dir = 'compression_level_parallel_1' # the compressed data of your choice

xarray_var = 'time'
var_to_extract = 'T_2M'
out_dir = 'test_output'

timings = {}
timings_cdo = {}
for data_dir in [reg_data_dir, compr_data_dir]:

    dataset = os.listdir(reg_data_dir)
    dataset_length = len(dataset)

    for file_name in dataset:
        timings[data_dir] = timings.get(data_dir, [])

        start_time = time.time()
        dt = xr.open_dataset(f'{data_dir}/{file_name}')
        dt[xarray_var].mean()
        end_time = time.time()

        runtime = end_time - start_time
        timings[data_dir].append(runtime)

    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)

    for file_name in dataset:
        timings_cdo[data_dir] = timings_cdo.get(data_dir, [])

        start_time = time.time()
        os.system(f'cdo -select,name={var_to_extract} {data_dir}/{file_name} {out_dir}/{file_name}')
        end_time = time.time()

        runtime = end_time - start_time
        timings_cdo[data_dir].append(runtime)

    shutil.rmtree(out_dir)



for key in timings.keys():

    vals = timings[key]
    mean_val = np.mean(vals)
    std_val = np.std(vals)

    print(f'For dataset {key}, the mean runtime per sample for xarray is {mean_val} +/- {std_val}')

for key in timings_cdo.keys():
    
    vals = timings[key]
    mean_val = np.mean(vals)
    std_val = np.std(vals)

    print(f'For dataset {key}, the mean runtime per sample for CDO is {mean_val} +/- {std_val}')


