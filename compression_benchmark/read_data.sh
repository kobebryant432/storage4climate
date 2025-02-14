#!/bin/bash -l

#SBATCH -A 2022_202
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=02:00:00

# read in via data
module purge
<load a Python venv or a conda env with xarray here>
module load CDO/2.3.0-iimpi-2022a

python read_data.py
