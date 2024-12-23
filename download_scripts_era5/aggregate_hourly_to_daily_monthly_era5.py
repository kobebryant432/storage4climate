# Script to merge hourly ERA5 or ERA5-Land into daily or monthly
# with relevant statistics taken. 

"""
credits: based on the step1_convert_era5_to_daily_monthly.txt R script by Bert Van Schaeybroeck, edited by Inne Vanderkelen, August 2024
"""


import os
import subprocess
import shutil

import pandas as pd


# Directories setup
dir_base = "/dodrio/scratch/projects/2022_200/external/"

# Variables initialization
aggregation_method = ["mean","max", "min"] # other options: "min", "sum". calculate aggregation statistics 
dataset = "era5"  # "era5-land"
domain = "europe"  # "europe"
init_yr = 1940
end_yr = 2023

var_name_lst = ["2m_dewpoint_temperature"]

amt_fun = len(aggregation_method)

amt_var = len(var_name_lst)
yr_lst = range(init_yr, end_yr + 1)
amt_yr = len(yr_lst)

time_freq_hr = "hourly"  # Or whichever time frequency is applicable
time_freq_day = "daily"
time_freq_mon = "monthly"


for var_to_use in var_name_lst:
    print(f"dataset: {dataset}, var: {var_to_use}")
    dir_base_var_hr = os.path.join(dir_base, dataset, domain, var_to_use, time_freq_hr) 
    dir_base_var_day = os.path.join(dir_base, dataset, domain, var_to_use, time_freq_day) 
    os.makedirs(dir_base_var_day, exist_ok=True)
    dir_base_var_mon = os.path.join(dir_base, dataset, domain, var_to_use, time_freq_mon) 
    os.makedirs(dir_base_var_mon, exist_ok=True)
    if dataset == "era5-land": 
        df_vars = pd.read_csv('era5-land_vars.csv')
        flag_cumul = df_vars.loc[df_vars['name.long'] == var_to_use,'cumul'] ==1
    else: 
        flag_cumul = False
    for yr_to_use in yr_lst:
        file_base_hr = f"{var_to_use}_{dataset}_{domain}_{time_freq_hr}_{yr_to_use}.nc"
        file_hr = os.path.join(dir_base_var_hr, file_base_hr)

        if os.path.exists(file_hr):
            print(f"var: {var_to_use}, year: {yr_to_use}")

            if flag_cumul:
                file_tmp1 = os.path.join(scratch_dir_to_use, f"{file_base_hr}.tmp1")
                file_tmp2 = os.path.join(scratch_dir_to_use, f"{file_base_hr}.tmp2")
                file_tmp3 = os.path.join(scratch_dir_to_use, f"{file_base_hr}.tmp3")
                subprocess.run(f"cdo -b F64 -shifttime,-1hour -selhour,1 {file_hr} {file_tmp1}", shell=True)
                subprocess.run(f"cdo -b F64 -shifttime,-1hour -selhour,0,2/23 -deltat {file_hr} {file_tmp2}", shell=True)
                subprocess.run(f"cdo -mergetime {file_tmp1} {file_tmp2} {file_tmp3}", shell=True)
                os.remove(file_tmp1)
                os.remove(file_tmp2)
            elif var_to_use == "10m_v_component_of_wind":
                file_tmp1 = file_hr.replace("_v_", "_u_")
                file_tmp2 = os.path.join(scratch_dir_to_use, f"{file_base_hr}.tmp2")
                file_tmp3 = os.path.join(scratch_dir_to_use, f"{file_base_hr}.tmp3")
                subprocess.run(f"cdo merge {file_hr} {file_tmp1} {file_tmp2}", shell=True)
                subprocess.run(f"cdo expr,'v10=sqrt(u10*u10+v10*v10)' {file_tmp2} {file_tmp3}", shell=True)
                os.remove(file_tmp2)
            elif var_to_use == "10m_u_component_of_wind":
                file_tmp1 = file_hr.replace("_u_", "_v_")
                file_tmp2 = os.path.join(scratch_dir_to_use, f"{file_base_hr}.tmp2")
                file_tmp3 = os.path.join(scratch_dir_to_use, f"{file_base_hr}.tmp3")
                subprocess.run(f"cdo merge {file_hr} {file_tmp1} {file_tmp2}", shell=True)
                subprocess.run(f"cdo expr,'u10=sqrt(u10*u10+v10*v10)' {file_tmp2} {file_tmp3}", shell=True)
                os.remove(file_tmp2)
            else:
                file_tmp3 = file_hr

            for fun_to_use in aggregation_method:
                print(aggregation_method)

                file_day = os.path.join(dir_base_var_day, f"{var_to_use}_{dataset}_{domain}_{time_freq_day}_{fun_to_use}_{yr_to_use}.nc")
                
                if os.path.exists(file_day):
                    print(f"{file_day}  already exists.")
                else:
                    subprocess.run(f"cdo -z zip day{fun_to_use} {file_tmp3} {file_day}", shell=True)


                # for now only monthly means, additional statistics can be added
                file_mon = os.path.join(dir_base_var_mon, f"{var_to_use}_{dataset}_{domain}_{time_freq_mon}_mean_{yr_to_use}.nc")

                if os.path.exists(file_mon):
                    print(f"{file_mon}  exists.")
                else:
                    subprocess.run(f"cdo -z zip monmean {file_day} {file_mon}", shell=True)

            if flag_cumul:
                os.remove(file_tmp3)



