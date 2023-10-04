import pandas as pd
import re
import ast

def aggregate_item_quantities(df, filter_day, ordered_type):
    # Filter the DataFrame
    filtered_df = df[(df['ordered_day'] == filter_day) & (df['ordered_type'] == ordered_type)]
    
    # Extract the 'ordered_items_list' column and evaluate it as lists
    ordered_items_series = filtered_df['ordered_items_list'].apply(ast.literal_eval)
    
    # Initialize a dictionary to store item quantities
    item_quantities = {}
    
    # Iterate through each row and process the 'ordered_items_list'
    for ordered_items_list in ordered_items_series:
        for item_desc in ordered_items_list:
            # Extract item name and quantity using regular expressions
            match = re.search(r'^(.*?) (\d+)$', item_desc)
            if match:
                item_name = match.group(1)
                quantity = int(match.group(2))
                
                # Update the item quantities in the dictionary
                item_quantities[item_name] = item_quantities.get(item_name, 0) + quantity
    
    # Create a DataFrame from the aggregated item quantities
    result_df = pd.DataFrame(item_quantities.items(), columns=['Item', 'Quantity'])
    
    # Sort the DataFrame by item name
    result_df = result_df.sort_values(by='Item')
    
    return result_df

def main():
    df = pd.read_excel('order_counts.xlsx')
    
    filter_day = 'Thursday'
    ordered_type = 'DINNER'
    
    result_df = aggregate_item_quantities(df, filter_day, ordered_type)
    sorted_df = result_df.sort_values(by='Quantity', ascending=False)
    sorted_df.to_excel(f'item_counts_{filter_day}_{ordered_type}.xlsx', index=False)

if __name__ == "__main__":
    main()
