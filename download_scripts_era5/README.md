# Downloading ERA5 data in the Storage4Climate repository

## Overview

This directory contains scripts for downloading ERA5 and ERA5-Land data in the shared data directory on the Storage4Climate data directory. These scripts are designed to help users efficiently retrieve and process climate data for their research and analysis needs, building the shared ERA5 dataset. 

On Tier-1 scratch, these data is located under: 
    ```bash
    /dodrio/scratch/projects/2022_200/external/era5
    ```

## Installation

Before using the scripts in this directory, you need to set up the `env_era5` Python environment. Follow the steps below to install the environment:

1. **Clone the repository**:
    ```bash
    git clone git@github.com:VUB-HYDR/storage4climate.git
    cd storage4climate/download_scripts_era5
    ```

2. **Create and activate the Python environment**:
All packages necessary to download and process ERA5 data (including the [CDS API client](https://cds.climate.copernicus.eu/how-to-api) ) are in the `env_era5.yml` Python environment. Install the environment as follows: 

    ```bash
    conda env create -f env_era5.yml
    conda activate env_era5
    ```

3. **Setup the CDS API personal access token**:
Follow the instructions outlined on the ['how-to-api'](https://cds.climate.copernicus.eu/how-to-api) in Step 1 to setup your personal CDS API access token. This is necessary for connecting to the CDS for downloading ERA5. 

## Usage

Once the `env_era5` environment is set up, you can use the scripts in this directory to download era5 and era5-land data. Each script is designed for specific tasks and can be executed as follows:

### **1. Downloading hourly ERA5**
Downloads era5 data for a specified variable, domain, years date range [`download_era5_single_level.py`](./download_era5_single_level.py)

```bash
python download_era5_single_level.py
```

The download might take a lot of time, so you can also submit it as a bash job to let it download in the background using the [`download_era5_single_level.pbs`](./download_era5_single_level.pbs)

```bash
sbatch download_era5_single_level.pbs
```

> Note: The download script downloads only the hourly files (raw data fromat), the aggregation into daily or monthly files happens in step 2. 



### **2. Aggregating hourly ERA5 data to daily and monthly**

Processes the downloaded climate data.

```bash
python process_data.py --input-file <path_to_downloaded_file>
```

## Additional Information

- Ensure that you have the necessary permissions to access and download the data.
- For detailed information on each script, refer to the comments and documentation within the script files.

## Support

If you encounter any issues or have questions, please contact the repository maintainer.

## Open issues/contributing

Feel free to contribute to these scripts by issuing pull requests. 

Stading issues: 
- downloading and aggregating pressure level data
- monthly aggregation: add additional aggregation methods to mean. 
