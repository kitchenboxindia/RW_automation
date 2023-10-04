import pandas as pd

# Sample data
data = {
    'item_dicts': [
        [{'item_name': 'Steam Rice Egg Curry & Kheer Thali', 'item_quantity': '2'}],
        [{'item_name': 'Double Egg Chicken Hakka Noodles', 'item_quantity': '1'}],
        [{'item_name': 'Tawa Paratha Veg Curry & Desert Thali', 'item_quantity': '1'}],
        [{'item_name': 'Tawa Paratha', 'item_quantity': '1'}, {'item_name': 'Dhaba Style Double Anda Tadka', 'item_quantity': '1'}],
        [{'item_name': 'Tawa Paratha', 'item_quantity': '1'}, {'item_name': 'Dhaba Style Double Anda Tadka', 'item_quantity': '1'}],
        [{'item_name': 'Kukuda (6 Pcs) Alu Jhola', 'item_quantity': '1'}],
    ]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Initialize dictionaries to store item_name and its corresponding item_quantity sum
item_name_quantity_dict = {}

# Iterate through rows in the DataFrame
for index, row in df.iterrows():
    item_dicts = row['item_dicts']
    
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

# Create a new DataFrame with the summed item quantities
result_df = pd.DataFrame(item_name_quantity_dict.items(), columns=['item_name', 'item_quantity'])

print(result_df)
