import pandas as pd
from scipy.stats import zscore
import datetime
import matplotlib.pyplot as plt

# Function to convert quarter-year to datetime
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

# Load the actuals and forecast data
actuals_data = pd.read_excel("platform_3m_actuals_new.xlsx")
forecast_data = pd.read_csv("mviai_platform_3m_forecast.csv")

# Filter for '8k_Chassis' Platform
actuals_data = actuals_data[actuals_data['Platform'] == 'NCS_Fixed - 4.8T']
forecast_data = forecast_data[forecast_data['Platform'] == 'NCS_Fixed - 4.8T']

print("Actuals Data:")
print(actuals_data)

print("Forecast Data:")
print(forecast_data)

# Convert the quarter-year to datetime
actuals_data['qtr'] = actuals_data['qtr'].apply(convert_qtr_to_date)
forecast_data['qtr'] = forecast_data['qtr'].apply(convert_qtr_to_date)

# Merge the actuals and forecast data by quarter
merged_data = pd.merge(actuals_data, forecast_data, on=['Platform','qtr'], how='outer')

# Drop the NaN values
merged_data = merged_data.dropna()

# Calculate the Z-scores for the 'Bookings_3m' column in the actuals data
merged_data['Z_score'] = zscore(merged_data['Bookings_3m'])

# Define the confidence interval (e.g., 95% corresponds to 1.96 standard deviations)
confidence_interval = 1.96

# Identify the outliers in the forecast data
merged_data['Outlier'] = (merged_data['Z_score'] < -confidence_interval) | (merged_data['Z_score'] > confidence_interval)

# Cap the outliers at the closest boundary of the confidence interval
mean = merged_data['Bookings_3m'].mean()
std_dev = merged_data['Bookings_3m'].std()

# Store the adjusted forecasts in a new column 'Adjusted_Forecast_3m'
merged_data['Adjusted_Forecast_3m'] = merged_data['Forecast_3m']
merged_data.loc[merged_data['Z_score'] < -confidence_interval, 'Adjusted_Forecast_3m'] = mean - confidence_interval * std_dev
merged_data.loc[merged_data['Z_score'] > confidence_interval, 'Adjusted_Forecast_3m'] = mean + confidence_interval * std_dev

# Print the merged data with the adjusted forecasts
print(merged_data)

# Save the adjusted data to a CSV file
merged_data.to_csv('merged_data_adjusted.csv')

# Create a plot
plt.figure(figsize=(10,6))
plt.plot(merged_data['qtr'], merged_data['Bookings_3m'], label='Actuals')
plt.plot(merged_data['qtr'], merged_data['Forecast_3m'], label='Forecast')
plt.plot(merged_data['qtr'], merged_data['Adjusted_Forecast_3m'], label='Adjusted Forecast')
plt.fill_between(merged_data['qtr'], mean - confidence_interval * std_dev, mean + confidence_interval * std_dev, color='b', alpha=.1)
plt.legend()
plt.show()
