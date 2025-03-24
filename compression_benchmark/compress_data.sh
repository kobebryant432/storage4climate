#!/bin/bash -l

#SBATCH -A 2022_202
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --time=12:00:00

data_path='test_data' # path to your input data
output_path='<your_path>'
N=128                 # number of processes. Normally the same as your ntasks-per-node

module load NCO/5.1.9-intel-2022a

files=($(ls $data_path))

original_dir_size=$(du -sh test_data)
echo "The size of test_data is ${original_dir_size}"

compression_levels=(1 2 3 4 5 6 7 8 9)

for level in "${compression_levels[@]}"; do

    compress_dir="${output_path}/compression_level_parallel_${level}"
    mkdir -p ${compress_dir}

    time for file in "${files[@]}"; do

        ((i=i%N)); ((i++==0)) && wait
        nccopy -d $level "test_data/${file}" "${compress_dir}/${file}" &
    done
	
	dir_size=$(du -sh ${compress_dir})
	
	echo "The size of ${compress_dir} is ${dir_size}"
	
done


