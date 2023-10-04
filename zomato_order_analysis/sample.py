import pandas as pd
from datetime import datetime, timedelta

# Specify the path to your Excel file
excel_file_path = 'result/order_counts.xlsx'

# Read the Excel file into a DataFrame
df = pd.read_excel(excel_file_path)

# Extract the start_date from the first row
start_date = df['ordered_date_time'].iloc[0]

# Extract the end_date from the last row
end_date = df['ordered_date_time'].iloc[-1]

# Create a date range from start_date to end_date
date_range = pd.date_range(start=start_date, end=end_date)

# Initialize a dictionary to store day counts
day_counts = {
    'Sunday': 0, 'Monday': 0, 'Tuesday': 0, 'Wednesday': 0,
    'Thursday': 0, 'Friday': 0, 'Saturday': 0
}

# Iterate through the date range and count each day of the week
for date in date_range:
    day_of_week = date.strftime('%A')
    day_counts[day_of_week] += 1

# Print the counts
print(day_counts)

# Convert the dictionary to a DataFrame
day_counts_df = pd.DataFrame(list(day_counts.items()), columns=['Day', 'Count'])

print(day_counts_df)
