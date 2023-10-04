import pandas as pd
from datetime import datetime
import re

def concatenate_values(row):
    item_name = row['Item1-name_reward_type_quantity_price+Variants+Addons']
    
    # Iterate through columns that start with 'Unnamed' and concatenate their values with "  "
    for col_name, col_value in row.items():
        if col_name.startswith('Unnamed') and not pd.isna(col_value):
            item_name += '**' + str(col_value)  # Convert float to string
    
    return item_name

def clean_item(item):
    cleaned_item = item.split('+')[0].replace('_NA_', ' ').replace('_', ' ')
    return cleaned_item

def get_weekday(date_str):
    try:
        date = datetime.strptime(str(date_str), '%Y-%m-%d %H:%M:%S')
        return date.strftime('%A')  # Return the full weekday name
    except ValueError:
        return None


def create_item_dicts(split_items):
    item_dicts = []
    for item in split_items:
        parts = item.split(' ')
        if len(parts) >= 2:
            item_name = ' '.join(parts[:-2])
            item_quantity = parts[-2]
            item_dicts.append({'item_name': item_name, 'item_quantity': item_quantity})
    return item_dicts


def extract_item_data(df):
    # Initialize empty lists to store the extracted data
    item_names = []
    item_quantities = []
    week_days = []

    # Iterate through rows in df
    for index, row in df.iterrows():
        week_day = row['week_day']
        item_dicts = row['item_dicts']

        # Create a dictionary to store item_name and its corresponding total quantity
        item_name_quantity_dict = {}

        # Iterate through the item_dicts list for each row
        for item_dict in item_dicts:
            item_name = item_dict['item_name']
            item_quantity = item_dict['item_quantity']

            # Extract valid integers from item_quantity, e.g., '(4' -> '4'
            item_quantity = ''.join(filter(str.isdigit, item_quantity))

            # Convert to int for summation
            item_quantity = int(item_quantity) if item_quantity else 0

            # Add the item_quantity to the existing value (if it exists) or set it as the initial value
            if item_name in item_name_quantity_dict:
                item_name_quantity_dict[item_name] += item_quantity
            else:
                item_name_quantity_dict[item_name] = item_quantity

        # Append the data to the respective lists
        for item_name, item_quantity in item_name_quantity_dict.items():
            item_names.append(item_name)
            item_quantities.append(item_quantity)
            week_days.append(week_day)

    # Create a new DataFrame with the extracted data
    new_df = pd.DataFrame({'item_name': item_names, 'item_quantity': item_quantities, 'week_day': week_days})
    return new_df


def main():
    # Read the Excel file and skip rows
    df = pd.read_excel('aug-sept_orders.xlsx', skiprows=5, converters={'Order ID': int})
    df.columns = df.columns.str.strip()

    # Define the columns to keep
    columns_to_keep = ['Order ID', 'Order-relay-time(ordered time)', 'Total-bill-amount <bill>', 'Item-count', 'Item1-name_reward_type_quantity_price+Variants+Addons'] + [f'Unnamed: {i}' for i in range(31, 35)]

    # Drop all other columns
    df = df[columns_to_keep]

    # Apply the function to create the 'item_name' column
    df['item_name'] = df.apply(concatenate_values, axis=1)

    # Apply the function to create the 'item_analysed' column
    df['item_analysed'] = df['item_name'].apply(lambda x: x.split('**'))

    # Clean each item in the 'item_analysed' column and join them back into a single string
    df['cleaned_item'] = df['item_analysed'].apply(lambda items: ', '.join([clean_item(item) for item in items]))

    # Add a new column 'week_day' representing the weekday of 'Order-relay-time(ordered time)'
    df['week_day'] = df['Order-relay-time(ordered time)'].apply(get_weekday)

    # Fill missing 'week_day' values with the weekday of the previous row
    df['week_day'].fillna(method='ffill', inplace=True)

    # Split each item in the 'cleaned_item' column by commas
    df['split_items'] = df['cleaned_item'].apply(lambda x: x.split(', '))

    # Create dictionaries for each item in the 'split_items' column
    df['item_dicts'] = df['split_items'].apply(create_item_dicts)
    df.to_excel('order_summary.xlsx', index=False)
    
    columns_to_filter = ['Order ID', 'Order-relay-time(ordered time)', 'Total-bill-amount <bill>', 'Item-count', 'week_day', 'item_dicts']
    filtered_df = df[columns_to_filter]
    filtered_df.to_excel('filtered_order_summary.xlsx', index=False)
    
    # Filter the filtered_df with the given weekday
    desired_week_day = 'Wednesday'  # Replace with your desired week day
    filtered_df = df[df['week_day'] == desired_week_day]
    print(filtered_df)

    # Extract item data
    new_df = extract_item_data(filtered_df)

    # Save the DataFrames to Excel files
    filtered_df.to_excel('filtered-order_summary.xlsx', index=False)
    df.to_excel('order_summary.xlsx', index=False)
    new_df.to_excel('item_summary.xlsx', index=False)

    

if __name__ == "__main__":
    main()
