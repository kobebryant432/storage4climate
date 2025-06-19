#!/bin/bash

# Define the project name to extract data for
PROJECT_NAME="gpr_compute_2022_200"

cd "$(dirname "$0")"

# Define the output file
OUTPUT_FILE="data/file_usage.dat"

# Run the my_dodrio_quota command and parse the output
my_dodrio_quota | awk -v project="$PROJECT_NAME" -v date="$(date '+%Y-%m-%d %H:%M:%S')" '
    $0 ~ "Quota for project " project ":" {found=1} 
    found && /Filesystem/ {getline; print date, $6, $7; exit}
' >> "$OUTPUT_FILE"
