import fitz  # PyMuPDF
import re
import pandas as pd
import os
from datetime import datetime
from collections import defaultdict
import ast


def list_pdf_files():
    # Directory path
    directory_path = 'zomato_orders'
    # Initialize an empty list to store file names
    file_list = []
    # Iterate through all files in the directory
    for filename in os.listdir(directory_path):
        if os.path.isfile(os.path.join(directory_path, filename)):
            file_list.append(directory_path+'/'+filename)
    return file_list

def extract_text_from_pdf(pdf_path):
    text = ""
    pdf_document = fitz.open(pdf_path)
    
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text += page.get_text()
    pdf_document.close()
    return text

def extract_order_id(text):
    match = re.search(r"^Zomato order:.*$", text, re.MULTILINE)
    if match:
        extracted_line = match.group()
        order_id = extracted_line.split(": ")[1]
        return order_id
    return None

def extract_ordered_date_time(text):
    index_paid = text.find("PAID")
    if index_paid != -1:
        lines = text[:index_paid].strip().split('\n')
        if lines:
            ordered_date_time = lines[-1]
            ordered_date_time = ordered_date_time.replace('nd', '').replace('rd', '').replace('st', '').replace('th', '')
            # Convert the input string to a datetime object
            date_object = datetime.strptime(ordered_date_time, "%d %b %Y at %I:%M %p")
            # Get the day of the week as an integer (0 = Monday, 6 = Sunday)
            day_of_week = date_object.weekday()
            # Get the day name corresponding to the integer
            ordered_day = date_object.strftime("%A")
            ordered_time = ordered_date_time.split('at ')[-1]

            # Determine the order_type based on the ordered_time
            if 10 <= date_object.hour < 17:
                order_type = "LUNCH"
            elif 8 <= date_object.hour < 11:
                order_type = "BREAKFAST"
            elif 18 <= date_object.hour or date_object.hour < 0:
                order_type = "DINNER"
            else:
                order_type = "UNKNOWN"

            return ordered_date_time, ordered_day, ordered_time, order_type
    return None

def extract_ordered_items(text):
    pattern = r"Summary\n(.*?)Taxes"
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        ordered_items = matches[0].strip()
        single_line_ordered_items = ordered_items.replace('\n', ' ')
        whitespace_items_list = single_line_ordered_items.split("  ")
        ordered_items_list = [item.strip() for item in whitespace_items_list]
        ordered_items_list_processed = []
        for items in ordered_items_list:
            pattern = r'(.*?\d) x \d+ ₹\d+'
            match = re.match(pattern, items)

            if match:
                extracted_part = match.group(1)
                # print(extracted_part)
            else:
                print("No match found.")
            ordered_items_list_processed.append(extracted_part)
        return ordered_items_list_processed
    return None

def extract_total_amount(text):
    lines = text.split('\n')
    total_index = lines.index("Total")
    if total_index < len(lines) - 1:
        total_amount = lines[total_index + 1]
        return total_amount
    return None

def extract_promo_amount(text):
    try:
        lines = text.split('\n')
        promo_index = lines.index("Promo")
        if promo_index < len(lines) - 1:
            promo = lines[promo_index + 1]
            return promo
    except ValueError:
        pass  # Handle the ValueError here if needed
    return None

def aggregate_item_counts_weekday(data, filter_day=None):
    # Create a DataFrame
    df = pd.DataFrame(data)

    # Filter data based on ordered_day if filter_day is provided
    if filter_day:
        df = df[df['ordered_day'] == filter_day]

    # Initialize a dictionary to store item counts
    item_counts = defaultdict(int)

    # Regular expression to match item names and quantities
    item_pattern = re.compile(r'^(.*?) (\d+)$')

    # Iterate through each row in the DataFrame
    for _, row in df.iterrows():
        ordered_items_list = row['ordered_items_list']

        for item_info in ordered_items_list:
            match = item_pattern.search(item_info)
            if match:
                item_name = match.group(1)
                item_quantity = int(match.group(2))
                item_counts[item_name] += item_quantity
    
    # Create a DataFrame from the aggregated item counts
    result_df = pd.DataFrame(item_counts.items(), columns=['Item', 'Count'])
    
    # Add a column for ordered_day
    if filter_day:
        result_df['Ordered Day'] = filter_day
    
    return result_df

def aggregate_item_quantities_ordertype(df, filter_day, ordered_type):
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
    # Create the "result" folder if it doesn't exist
    if not os.path.exists('result'):
        os.makedirs('result')

    order_dict_list = []
    file_list = list_pdf_files()
    for pdf_path in file_list:
        print(f'Extracting data for {pdf_path}')
        print ('=============')
        extracted_text = extract_text_from_pdf(pdf_path)
        order_id = extract_order_id(extracted_text)
        if order_id:
            print(f'order_id: {order_id}')
        else:
            print("No order ID found.")

        ordered_date_time, ordered_day, ordered_time, ordered_type = extract_ordered_date_time(extracted_text)
        if ordered_date_time:
            print(f'ordered_date_time: {ordered_date_time}')
        else:
            print("No ordered date and time found.")

        if ordered_day:
            print(f'ordered_day: {ordered_day}')
        else:
            print("No ordered date and time found.")
        
        if ordered_time:
            print(f'ordered_time: {ordered_time}')
        else:
            print("No ordered date and time found.")

        if ordered_time:
            print(f'ordered_type: {ordered_type}')
        else:
            print("No ordered date and time found.")

        ordered_items_list_processed = extract_ordered_items(extracted_text)
        if ordered_items_list_processed:
            print(f'ordered_items_list: {ordered_items_list_processed}')
        else:
            print("No ordered items found.")

        total_amount = extract_total_amount(extracted_text)
        if total_amount:
            print(f'total_amount: {total_amount}')
        else:
            print("No total amount found.")

        promo_amount = extract_promo_amount(extracted_text)
        if promo_amount:
            print(f'promo: {promo_amount}')
        else:
            promo_amount = 0
            print(f'promo: {promo_amount}')
    
        order_dict = {
            'order_id': order_id,
            'ordered_date_time': ordered_date_time,
            'ordered_day': ordered_day,
            'ordered_time': ordered_time,
            'ordered_type': ordered_type,
            'ordered_items_list': ordered_items_list_processed,
            'total_amount': total_amount,
            'promo': promo_amount
        }
        order_dict_list.append(order_dict)
    
    # print(order_dict_list)
    order_df = pd.DataFrame(order_dict_list)
    order_df['ordered_date_time'] = pd.to_datetime(order_df['ordered_date_time'], format='%d %b %Y at %I:%M %p')

    # Sort DataFrame by "ordered_date_time"
    sorted_order_df = order_df.sort_values(by='ordered_date_time')
    excel_filename = f'result/order_counts.xlsx'
    sorted_order_df.to_excel(excel_filename, index=False)

    # Create a dictionary to map weekdays to their corresponding Excel filenames
    weekday_filenames = {
        'Sunday': 'item_counts_Sunday.xlsx',
        'Monday': 'item_counts_Monday.xlsx',
        'Tuesday': 'item_counts_Tuesday.xlsx',
        'Wednesday': 'item_counts_Wednesday.xlsx',
        'Thursday': 'item_counts_Thursday.xlsx',
        'Friday': 'item_counts_Friday.xlsx',
        'Saturday': 'item_counts_Saturday.xlsx'
    }

    # Create the "result" folder if it doesn't exist

    # Iterate through each weekday and create filtered Excel files
    for weekday in weekday_filenames.keys():
        result_df = aggregate_item_counts_weekday(order_df, weekday)
        # Sorting the DataFrame on the 'Count' column in ascending order
        sorted_df = result_df.sort_values(by='Count', ascending=False)
        # Save the DataFrame to an Excel file
        excel_filename = f'result/item_counts_{weekday}.xlsx'
        sorted_df.to_excel(excel_filename, index=False)

    # Iterate through each weekday and create Excel files for both LUNCH and DINNER
    for weekday in weekday_filenames.keys():
        for ordered_type in ['LUNCH', 'DINNER']:
            df = pd.read_excel('result/order_counts.xlsx')
            result_df = aggregate_item_quantities_ordertype(df, weekday, ordered_type)
            # Sorting the DataFrame on the 'Count' column in ascending order
            sorted_df = result_df.sort_values(by='Quantity', ascending=False)
            # Save the DataFrame to an Excel file with weekday and ordered_type in the name
            excel_filename = f'result/item_counts_{weekday}_{ordered_type}.xlsx'
            sorted_df.to_excel(excel_filename, index=False)

if __name__ == "__main__":
    main()
