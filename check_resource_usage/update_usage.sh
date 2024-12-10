#!/bin/bash
project_name=$1

# If the project name is not provided, use the default project name
if [ -z "$project_name" ]; then
    project_name="2022_205"
fi

#Ensure the script is run from the correct directory
cd "$(dirname "$0")"

# Get the csv file from the project
file=/dodrio/scratch/projects/$project_name/.resource_app.usage.export.csv
git_dir=$(git rev-parse --show-toplevel)
input_file=$git_dir/VSC_monitoring/input/usage_$(date +"%Y%m%d").csv

cp $file $input_file

# Remove all lines before the line containing "Project Usages" but keep the line itself
sed -i '1,/Project Usages/{/Project Usages/!d}' $input_file

# Add and commit the changes
git pull
git add $input_file
git commit -m "Add usage data for project $project_name"
git push

#A github action will run python script and update the usage.
