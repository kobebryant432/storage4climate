#!/bin/bash

source ~/.bashrc

module load scikit-learn
module load matplotlib/3.7.2-gfbf-2023a

cd "$(dirname "$0")"

bash parse_file_number.sh
 
python plot_file_usage.py

git pull
git add plots/file_usage_plot.png
git commit -m "Add usage data for all projects"
git push
