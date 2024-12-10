#Import the csv file as pandas dataframe
import pandas as pd
pd.options.mode.copy_on_write = True
import matplotlib.pyplot as plt
import glob
import seaborn as sns
from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt

def millions(x, pos):
    'The two args are the value and tick position'
    return '%1.1fM' % (x * 1e-6)

mil_formatter = FuncFormatter(millions)

#########################
#        Inputs         #
#########################

#Get the git directory
import os

git_dir = os.popen('git rev-parse --show-toplevel').read().strip()
path = rf'{git_dir}/VSC_monitoring/input'
all_files = glob.glob(f'{path}/*.csv')

current_quarter = 'Q3'
quarter_credits = {'Q1': 6200000, 'Q2': 5000000, 'Q3': 5000000, 'Q4': 4600000}

#Create an extra plot showing the total credits requested vs the total credits used per user and in total
requested_per_user = {
    "vsc46032": 12756800,
    "vsc45263": 2467726,
    "vsc45628": 5111550,
    "vsc45381": 1670600,
    "vsc46275": 114282,
    "vsc44757": 5990489,
}

date= pd.to_datetime('today').strftime('%Y%m%d')

#########################
#     Pre-processing    #
#########################

df = pd.read_csv(all_files[0], header=1)

#Get the index of the row containing project logs in resource column
index_logs = df[df['Resource'] == 'Project Logs'].index[0]
df_overview = df[:index_logs]
df_credits = df_overview[df_overview['Resource'] == 'credits']
df_credits['Total_used'] = df_credits['Current used by user'].str.replace(' Hours', '').astype(float)
df_credits['Cumulative_used_by_user'] = df_credits['Total used by user'].str.replace(' Hours', '').astype(float)
df_credits['Cumulative_total_used'] = df_credits['Total used'].str.replace(' Hours', '').astype(float)
df_credits['Date'] = pd.to_datetime(df_credits['Date'], format='%d/%m/%Y - %H:%M').dt.date
df_credits = df_credits.sort_values(by='Date')

Total_credits = sum(quarter_credits.values())

#Make a dictionary with the remaining credits per quarter by subtracting the total used from the total credits per quarter until there are no credits left
remaining_credits = quarter_credits.copy()
total_used = sum(df_credits['Total_used'])
for key in remaining_credits.keys():
    if total_used > 0:
        if remaining_credits[key] > total_used:
            remaining_credits[key] -= total_used
            total_used = 0
        else:
            total_used -= remaining_credits[key]
            remaining_credits[key] = 0

remaining_credits['Used'] = sum(df_credits['Total_used'])

##########################
#   Plotting the data    #    
##########################
def pie_labels(data: dict):
    return [f'{key} \n ({value * 1e-6:.1f}M hours)' for key, value in data.items()]

#Set the style of the plots 
sns.set_theme(style='whitegrid')

#Make a plot with 4 subplots
fig, axs = plt.subplots(2, 2, figsize=(15, 10))

#Fig 1: sns pie-chart showing the total used and the remaining credits the remaining credits per quarter
axs[0, 0].pie(remaining_credits.values(), labels=pie_labels(remaining_credits), autopct='%1.1f%%')
axs[0, 0].set_title(f'Total used and remaining credits (per quarter)')

#Fig 2: pie-chart showing the used and unused credits for the current quarter
data = {'Unused': remaining_credits[current_quarter], 'Used': quarter_credits[current_quarter] - remaining_credits[current_quarter]}
axs[0, 1].pie(data.values(), labels=pie_labels(data), autopct='%1.1f%%')
axs[0, 1].set_title(f'Credit usage: {current_quarter}')

#Fig 3: sns bar-chart showing the total used in function of time (grouped by day) and the cumulative total used
sns.lineplot(x='Date', y='Cumulative_used_by_user', data=df_credits, hue='User', ax=axs[1, 0])
sns.lineplot(x='Date', y='Cumulative_total_used', data=df_credits, color='red', ax=axs[1, 0], label='Total used')

axs[1, 0].set_ylabel('Credits (hours Million)')
axs[1, 0].yaxis.set_major_formatter(mil_formatter)
axs[1, 0].set_title('Total used over time')
axs[1, 0].tick_params(axis='x', rotation=45)

#Fig 4: sns bar-chart showing the total used credits per user
df_users = df_credits.groupby('User')["Total_used"].sum().reset_index()
sns.barplot(x='User', y='Total_used', data=df_users, ax=axs[1, 1])
axs[1, 1].set_ylabel('Credits (hours Million)')
axs[1, 1].yaxis.set_major_formatter(mil_formatter)
axs[1, 1].set_title('Total used per user')
axs[1, 1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.subplots_adjust(bottom=0.2)
plt.savefig(f'{git_dir}/VSC_monitoring/output/monitoring.png')
plt.show()

##########################
##      Extra plot      ##
##########################
#Additional plot to view the total requested credits vs the total used credits per user

df_users['Total_requested'] = df_users['User'].map(requested_per_user)
#Remove the users that have no requested credits
df_users['Total_remaining'] = df_users['Total_requested'] - df_users['Total_used']

#Get the sum of the total_used if total_requested is NaN
rest_users_use = df_users[df_users['Total_requested'].isna()]['Total_used'].sum()

#Drop the users that have no requested credits
df_req = df_users[['User', 'Total_requested', 'Total_used']].copy()
df_req = df_req.dropna()

#Add an all users row
df_req.loc[len(df_req)] = {"User": "All users", "Total_requested": Total_credits, "Total_used": sum(df_credits['Total_used'])}
df_req.loc[len(df_req)] = {"User": "Remaining users", "Total_requested": Total_credits - sum(requested_per_user.values()), "Total_used": rest_users_use}

df_req = df_req.sort_values(by='Total_requested', ascending=False)

#Plot the total requested amount as a bar plot with the total used amount as a bar plot on top of it

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x='User', y='Total_requested', data=df_req, ax=ax, color='blue', label='Requested', alpha=0.5)
sns.barplot(x='User', y='Total_used', data=df_req, ax=ax, color='red', label='Used', alpha=0.8)

#Add the percentage of the total used credits per user on top of the bars as text
for idx, row in df_req.iterrows():
    ax.text(row.User, row['Total_used'] + 0.1e6, f'{row["Total_used"] / row["Total_requested"] * 100:.1f}%', ha='center', va='bottom')


ax.set_ylabel('Credits (hours Million)')
ax.yaxis.set_major_formatter(mil_formatter)
ax.set_title('Requested and used credits')
ax.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'{git_dir}/VSC_monitoring/output/monitoring_users.png')

#Move the csv file to the output archive folder
import shutil
shutil.move(all_files[0], f'{git_dir}/VSC_monitoring/archive/')
shutil.copy(f'{git_dir}/VSC_monitoring/output/monitoring.png', f'{git_dir}/VSC_monitoring/archive/{current_quarter}_{date}_monitoring.png')
shutil.copy(f'{git_dir}/VSC_monitoring/output/monitoring_users.png', f'{git_dir}/VSC_monitoring/archive/{current_quarter}_{date}_monitoring_users.png')

