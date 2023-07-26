import pandas as pd
from scipy.stats import zscore

# Define the data path
data_path = "platform_3m_actuals_new.xlsx"  # Replace with the path to your data file

# Load the data
data = pd.read_excel(data_path)

# Calculate the Z-score for the 'Bookings_3m' column
data['zscore'] = zscore(data['Bookings_3m'])

# Define a threshold for outliers
threshold = 3

# Create a new column 'cluster' and assign the labels 'Outlier' or 'Non-outlier' based on the Z-score
data['cluster'] = ['Outlier' if abs(z) > threshold else 'Non-outlier' for z in data['zscore']]

# Display the dataframe
#print(data)

#display only the outliers
print(data[data['cluster'] == 'Outlier'])


