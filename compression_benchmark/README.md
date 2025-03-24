# Compression benchmark netCDF

## About
This directory contains some scripts to test what `nccopy` compression level is the best for your data. It will basically loop over all available compression
levels (1-9, with 1 being the least compression and 9 being the highest level of compression). Next to that, there is also a Python script that measures the speed
of reading the compressed data with both xarray and CDO. This is then compared with the speed of reading the uncompressed data. This last test is optional,
as the expectation is that there is no significant difference in reading speed. First tests did confirm this.

## Set-up

1. Clone this repository locally
2. Select a relevant test dataset. You should choose data that represents most of your data, i.e. containing variables that are present in all or most of your data, similar size... The dimensions of variables (1D, 2D, 3D), might have a big impact on the possible level of compression. If your datasets are very different, it is recommended to conduct multiple tests.
3. Take a subset of your dataset. As most of you work with very large datasets, it would take too much time to run this benchmark over your full dataset. The initial tests were run over a month of data, with hourly files. Copy this subset somewhere on **scratch** storage. 
4. Open the `compress_data.sh` file and modify the `data_path` and the `output_path` variables, where `data_path` is the path to your data subset, and the `output_path` the path where you would like to store the compressed output data. Make sure that both directories are located on scratch storage for the best performance. If you want, you can also modify the number of parallel processes `N` (but be careful that this is not higher than the `--ntasks-per-node` Slurm parameter). If you would notice you run into memory issues, you can also increase the default memory per node with `#SBATCH --mem-per-cpu=...`
5. Run the script with `sbatch compress_data.sh`. The script will create an output directory `compression_level_parallel_${level}` in `$output_path` for each of the compression levels. It will also calculate the size of each of these directories with `du -sh`. The results are just written to the Slurm output file, and not parsed further, but feel free to add this to the script if you want. The compression process is also timed, making it possible for you to find a balance between compression level and the time to compress.

(optional)
6. If you would like to test the time to read your compressed data, you can use the two other scripts included. They might require some changes to be relevant for your data. You can start by opening the `read_data.py` file and changing the `reg_data_dir` and `compr_data_dir` to the paths of your uncompressed test data and the compressed data of your choice (basically the level of compression you chose in the previous step). Also change the `out_dir`, to a path where you want to place the `cdo` output data. Further on, you might have to change the `xarray_var` and the `var_to_extract` variables, which will determine what xarray variable you want to do a calculation on (mean in this case), and what variable you want to extract with CDO, respectively. Have a look at the code used, as you might want to change the measured commands to be more relevant to your case. 
7. Close the python file and open the `read_data.sh` file. Here you have to add a Python venv or Conda env (containing xarray) on the `<load a Python venv or a conda env with xarray here>` line.
8. Run the `read_data.sh` file with `sbatch read_data.sh`. The output of this job will contain runtimes for both the CDO and xarray read commands, both for the compressed and uncompressed data.

## Some notes
- A higher compression level (1-9) should give a better compression. You might notice that the compression rate stops increasing after a certain level though. This means you have reached the highest level of compression that is possible for your data (with `nccopy` anyway). In that case you can choose the lowest level of compression that has this compression rate. 
- Higher compression levels take more time to process, and the percentage of compression per level should also decrease, meaning that there might be an optimum for your data somewhere, hence the reason to time each of the compression steps.
- Feel free to modify the script to use other compression methods (e.g. nccompress). `nccopy` has the downside that it creates a copy instead of compressing in place.
- As mentioned above, the `read_data.py` script can be modified to better fit your usecases. Be sure to take a function that limits itself to reading the data, but also actually reads the data. For xarray for example, you see that we do a mean calculation of a variable. This is because `xr.open_dataset` function does not yet read the data inside the netcdf file. You need this extra step to really pull the data in.
