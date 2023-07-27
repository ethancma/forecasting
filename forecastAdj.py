import pandas as pd
import datetime
import numpy as np

# Function to convert quarter to datetime
def convert_qtr_to_date(qtr):
    qtr, year = qtr.split('FY')
    if qtr == 'Q1':
        month = 1
    elif qtr == 'Q2':
        month = 4
    elif qtr == 'Q3':
        month = 7
    elif qtr == 'Q4':
        month = 10
    year = int(year) + 2000
    return datetime.datetime(year, month, 1)

# Load the data from the Excel file
df = pd.read_excel("platform_3m_actuals_new.xlsx")

# Filter out the data for the 8k_Chassis platform
df_8k_chassis = df[df['Platform'] == '8k_Chassis']

# Convert the 'qtr' column to datetime
df_8k_chassis['sdate'] = df_8k_chassis['qtr'].apply(convert_qtr_to_date)

# Calculate the mean and deviation over a rolling window of 3 quarters
df_8k_chassis = df_8k_chassis.sort_values(by="sdate")
df_8k_chassis['mean'] = df_8k_chassis['Bookings_3m'].rolling(window=3).mean()
df_8k_chassis['deviation'] = df_8k_chassis['Bookings_3m'].rolling(window=3).std()

# The naive mean and naive deviation are the last values from the 'mean' and 'deviation' columns
df_8k_chassis['naivemean'] = df_8k_chassis['mean'].shift(1)
df_8k_chassis['naivedeviation'] = df_8k_chassis['deviation'].shift(1)

# Calculate the lower limit and upper limit based on naivemean and naivedeviation
df_8k_chassis['lower limit'] = df_8k_chassis['naivemean'] - 3*df_8k_chassis['naivedeviation']
df_8k_chassis['upper limit'] = df_8k_chassis['naivemean'] + 3*df_8k_chassis['naivedeviation']

# Calculate the Z-score
df_8k_chassis['z_score'] = (df_8k_chassis['Bookings_3m'] - df_8k_chassis['naivemean']) / df_8k_chassis['naivedeviation']

# Identify outliers based on Z-score
df_8k_chassis['actuals_outlier'] = np.abs(df_8k_chassis['z_score']) > 3

# Adjust the outliers
df_8k_chassis['actuals_adjusted'] = df_8k_chassis.apply(
    lambda row: row['naivemean'] + 3*row['naivedeviation'] if row['z_score'] > 3
                else row['naivemean'] - 3*row['naivedeviation'] if row['z_score'] < -3
                else row['Bookings_3m'], axis=1
)

# Save to csv
df_8k_chassis.to_csv('8k_chassis_actuals_adjusted.csv', index=False)

# Load the forecast data
df_forecast = pd.read_csv("mviai_platform_3m_forecast.csv")

# Filter out the data for the 8k_Chassis platform
df_forecast = df_forecast[df_forecast['Platform'] == '8k_Chassis']

# Convert the 'qtr' column in the forecast data to datetime
df_forecast['fdate'] = df_forecast['qtr'].apply(convert_qtr_to_date)

# Sort the forecast data by 'fdate'
df_forecast = df_forecast.sort_values(by="fdate")

# Merge df_8k_chassis with df_forecast on the dates
df_8k_chassis = pd.merge(df_8k_chassis, df_forecast[['fdate', 'Forecast_3m']], left_on='sdate', right_on='fdate', how='left')

print(df_8k_chassis.head(10))

#save to csv
df_8k_chassis.to_csv('8k_chassis_actuals_adjusted_forecast.csv', index=False)
