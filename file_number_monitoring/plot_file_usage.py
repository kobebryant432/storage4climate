import pandas as pd
from datetime import datetime
from sklearn.linear_model import LinearRegression
import numpy as np
import os
import sys

import matplotlib.pyplot as plt

# Read the data
git_dir = os.popen('git rev-parse --show-toplevel').read().strip()

data_file = os.path.join(git_dir, 'file_number_monitoring/data/file_usage.dat')
data = pd.read_csv(data_file, sep='\s+', names=['date', 'time', 'files', 'quota'])

# Combine date and time into a single datetime column
data['datetime'] = pd.to_datetime(data['date'] + ' ' + data['time'])
data = data.sort_values('datetime')

# Plot the number of files over time
plt.figure(figsize=(10, 6))
plt.plot(data['datetime'], data['files'], label='Number of Files')
plt.axhline(y=data['quota'].iloc[-1], color='orange', linestyle='--', label='Quota')  # Add horizontal line for quota
plt.xlabel('Time')
plt.ylabel('Number of Files')
plt.title('Number of Files Over Time')
plt.ylim(top=data['quota'].iloc[-1]* 1.0001)  # Set Y-axis limit to 0.0a1% above the quota

# Format the Y-axis to show values in millions with 2 decimal places
plt.gca().get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x / 1e6:.2f}M'))

# Filter data for the 24 hours before the last entry
last_entry_time = data['datetime'].iloc[-1]
start_time = last_entry_time - pd.Timedelta(days=1)
last_day_data = data[(data['datetime'] >= start_time) & (data['datetime'] <= last_entry_time)]

# Perform linear regression on the last day's data
X = (last_day_data['datetime'] - last_day_data['datetime'].min()).dt.total_seconds().values.reshape(-1, 1)
y = last_day_data['files'].values
reg = LinearRegression().fit(X, y)

# Predict the trend for the last day
X_pred = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
y_pred = reg.predict(X_pred)
plt.plot(last_day_data['datetime'].min() + pd.to_timedelta(X_pred.flatten(), unit='s'), y_pred, label='Last Day Trend', color='red')

# Calculate the estimated time to reach the quota
if reg.coef_[0] > 0:  # Only calculate if the slope is positive
    current_files = data['files'].iloc[-1]
    quota = data['quota'].iloc[-1]
    time_to_quota = (quota - current_files) / reg.coef_[0]
    estimated_reach_time = last_day_data['datetime'].max() + pd.to_timedelta(time_to_quota, unit='s')
    plt.gcf().text(0.01, 0.01, 
                   f'Quota Reach: {estimated_reach_time.strftime("%Y-%m-%d %H:%M:%S")}', 
                   color='red', fontsize=10, verticalalignment='bottom', horizontalalignment='left')
else:
    plt.gcf().text(0.01, 0.01, 
                   'Quota not reachable with current trend', 
                   color='green', fontsize=10, verticalalignment='bottom', horizontalalignment='left')

plt.legend()
plt.tight_layout()

#Save the plot
output_dir = os.path.join(git_dir, 'file_number_monitoring/plots')
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, 'file_usage_plot.png')
plt.savefig(output_file)