"""
Convert BME688 .bmerawdata files to CSV format for training.
Extracts data from ALL 8 sensors.
Each row includes: sensor_id, temperature, humidity, gas_resistance, label
"""

import json
import csv
import os
import glob
import argparse

def extract_label_from_filename(filename):
    """
    Extract label from filename based on naming convention.
    """
    base_name = os.path.basename(filename)
    base_name = base_name.replace('.bmerawdata', '')
    
    # Check for air files
    if base_name.lower().startswith('air_'):
        return 'air'
    
    # Check for red wines (r_ prefix)
    if base_name.lower().startswith('r_'):
        parts = base_name.split('_')
        if len(parts) >= 2:
            wine_name = parts[1].lower()
            if wine_name == 'monastrell':
                return 'monastrel'
            if wine_name == 'toro':
                return 'toro'
            if wine_name == 'garnacha':
                return 'garnacha'
            return wine_name
    
    # Check for white wines (w_ prefix)
    if base_name.lower().startswith('w_'):
        # Handle patterns like w_novel.1, w_macabeo.1, etc.
        parts = base_name.split('_')
        if len(parts) >= 2:
            # Get the wine name part (remove anything after .)
            wine_part = parts[1].split('.')[0].lower()
            
            # Known white wines
            if wine_part == 'macabeo':
                return 'macabeo'
            if wine_part == 'novel':
                return 'novell'  # sau 'w_novell_1' – cum vrei să se numească în date
            # Add more white wines here
            return wine_part
    
    print(f"Could not auto-detect label for {filename}")
    print("Possible labels: air, toro, garnacha, monastrel, macabeo, novell")
    return input("Enter label: ").strip()

def convert_bmerawdata_to_csv(input_file, output_file, label):
    """
    Convert a single .bmerawdata file to CSV.
    Extracts data for ALL 8 sensors.
    """
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Get the data columns and data block
    raw_data_body = data['rawDataBody']
    data_columns = raw_data_body['dataColumns']
    data_points = raw_data_body['dataBlock']
    
    # Find indices of needed columns
    sensor_idx = None
    temp_idx = None
    humidity_idx = None
    gas_idx = None
    
    for i, col in enumerate(data_columns):
        col_name = col['name']
        if col_name == 'Sensor Index':
            sensor_idx = i
        elif col_name == 'Temperature':
            temp_idx = i
        elif col_name == 'Relative Humidity':
            humidity_idx = i
        elif col_name == 'Resistance Gassensor':
            gas_idx = i
    
    print(f"  Sensor index: {sensor_idx}")
    print(f"  Temperature index: {temp_idx}")
    print(f"  Humidity index: {humidity_idx}")
    print(f"  Gas resistance index: {gas_idx}")
    print(f"  Total points: {len(data_points)}")
    
    # Write to CSV with sensor_id column
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['sensor_id', 'temperature', 'humidity', 'gas_resistance', 'label'])
        
        row_count = 0
        for point in data_points:
            sensor_id = point[sensor_idx] if sensor_idx is not None else 0
            temperature = point[temp_idx] if temp_idx is not None else 0
            humidity = point[humidity_idx] if humidity_idx is not None else 0
            gas_resistance = point[gas_idx] if gas_idx is not None else 0
            
            row = [sensor_id, temperature, humidity, gas_resistance, label]
            writer.writerow(row)
            row_count += 1
    
    print(f"  Converted {row_count} rows")
    return row_count

def main():
    parser = argparse.ArgumentParser(description='Convert .bmerawdata files to CSV with all sensors')
    parser.add_argument('--input_dir', default='raw_data', help='Directory with .bmerawdata files')
    parser.add_argument('--output_dir', default='csv_data_all_sensors', help='Output directory for CSV files')
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Find all .bmerawdata files
    files = glob.glob(os.path.join(args.input_dir, "*.bmerawdata"))
    
    if not files:
        print(f"No .bmerawdata files found in {args.input_dir}")
        return
    
    print(f"Found {len(files)} files:")
    for f in files:
        print(f"  {os.path.basename(f)}")
    
    print("\n" + "-"*50)
    
    total_rows = 0
    for file in files:
        label = extract_label_from_filename(file)
        output_file = os.path.join(args.output_dir, 
                                   os.path.basename(file).replace('.bmerawdata', '.csv'))
        print(f"\nConverting {os.path.basename(file)} -> {os.path.basename(output_file)} (label={label})")
        try:
            rows = convert_bmerawdata_to_csv(file, output_file, label)
            total_rows += rows
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*50)
    print(f"Conversion complete! {total_rows} total rows saved to {args.output_dir}/")
    print("="*50)

if __name__ == "__main__":
    main()







# """
# Convert BME688 .bmerawdata files to CSV format for training.
# Extracts label from filename based on naming convention:
# - air_*.bmerawdata -> label = air
# - r_*.bmerawdata -> label = red wine name (garnacha, monastrel, toro)
# - w_*.bmerawdata -> label = white wine name (macabeo)
# """
# """
# Convert BME688 .bmerawdata files to CSV format for training.
# Structure: rawDataBody['dataColumns'] and rawDataBody['dataBlock'] (list of points)
# """

# import json
# import csv
# import os
# import glob
# import argparse

# def extract_label_from_filename(filename):
#     """
#     Extract label from filename based on naming convention.
#     """
#     base_name = os.path.basename(filename)
#     base_name = base_name.replace('.bmerawdata', '')
    
#     # Check for air files
#     if base_name.lower().startswith('air_'):
#         return 'air'
    
#     # Check for red wines (r_ prefix)
#     if base_name.lower().startswith('r_'):
#         parts = base_name.split('_')
#         if len(parts) >= 2:
#             wine_name = parts[1].lower()
#             if wine_name == 'monastrell':
#                 return 'monastrel'
#             if wine_name == 'toro':
#                 return 'toro'
#             if wine_name == 'garnacha':
#                 return 'garnacha'
#             return wine_name
    
#     # Check for white wines (w_ prefix)
#     if base_name.lower().startswith('w_'):
#         parts = base_name.split('_')
#         if len(parts) >= 2:
#             wine_name = parts[1].lower()
#             if wine_name == 'macabeo':
#                 return 'macabeo'
#             return wine_name
    
#     print(f"Could not auto-detect label for {filename}")
#     print("Possible labels: air, toro, garnacha, monastrel, macabeo")
#     return input("Enter label: ").strip()

# def convert_bmerawdata_to_csv(input_file, output_file, label):
#     """
#     Convert a single .bmerawdata file to CSV.
#     Each point is a list of values in the order of dataColumns.
#     """
#     with open(input_file, 'r') as f:
#         data = json.load(f)
    
#     # Get the data columns and data block
#     raw_data_body = data['rawDataBody']
#     data_columns = raw_data_body['dataColumns']
#     data_points = raw_data_body['dataBlock']  # This is a list of points
    
#     # Print column mapping for debugging (first time only)
#     print(f"  Found {len(data_columns)} columns")
    
#     # Column indices based on position in data_columns
#     # We need to find the index of each column by name
#     temp_idx = None
#     humidity_idx = None
#     gas_idx = None
    
#     for i, col in enumerate(data_columns):
#         col_name = col['name']
#         if col_name == 'Temperature':
#             temp_idx = i
#         elif col_name == 'Relative Humidity':
#             humidity_idx = i
#         elif col_name == 'Resistance Gassensor':
#             gas_idx = i
    
#     print(f"  Temperature index: {temp_idx}")
#     print(f"  Humidity index: {humidity_idx}")
#     print(f"  Gas resistance index: {gas_idx}")
#     print(f"  Total points: {len(data_points)}")
    
#     # Write to CSV
#     with open(output_file, 'w', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(['temperature', 'humidity', 'gas_resistance', 'iaq', 'label'])
        
#         row_count = 0
#         for point in data_points:
#             # point is a list of values
#             temperature = point[temp_idx] if temp_idx is not None else 0
#             humidity = point[humidity_idx] if humidity_idx is not None else 0
#             gas_resistance = point[gas_idx] if gas_idx is not None else 0
#             # IAQ not available in raw data, use a placeholder (optional)
#             iaq = 50 + (gas_resistance / 10000) if gas_resistance > 0 else 50
            
#             row = [temperature, humidity, gas_resistance, iaq, label]
#             writer.writerow(row)
#             row_count += 1
    
#     print(f"  Converted {row_count} rows")
#     return row_count

# def main():
#     parser = argparse.ArgumentParser(description='Convert .bmerawdata files to CSV')
#     parser.add_argument('--input_dir', default='raw_data', help='Directory with .bmerawdata files')
#     parser.add_argument('--output_dir', default='csv_data', help='Output directory for CSV files')
#     args = parser.parse_args()
    
#     # Create output directory
#     os.makedirs(args.output_dir, exist_ok=True)
    
#     # Find all .bmerawdata files
#     files = glob.glob(os.path.join(args.input_dir, "*.bmerawdata"))
    
#     if not files:
#         print(f"No .bmerawdata files found in {args.input_dir}")
#         return
    
#     print(f"Found {len(files)} files:")
#     for f in files:
#         print(f"  {os.path.basename(f)}")
    
#     print("\n" + "-"*50)
    
#     total_rows = 0
#     # Convert each file
#     for file in files:
#         label = extract_label_from_filename(file)
#         output_file = os.path.join(args.output_dir, 
#                                    os.path.basename(file).replace('.bmerawdata', '.csv'))
#         print(f"\nConverting {os.path.basename(file)} -> {os.path.basename(output_file)} (label={label})")
#         try:
#             rows = convert_bmerawdata_to_csv(file, output_file, label)
#             total_rows += rows
#         except Exception as e:
#             print(f"  ERROR: {e}")
#             import traceback
#             traceback.print_exc()
    
#     print("\n" + "="*50)
#     print(f"Conversion complete! {total_rows} total rows saved to {args.output_dir}/")
#     print("="*50)

# if __name__ == "__main__":
#     main()



# #python convert_bmerawdata_to_csv.py --input_dir raw_data --output_dir csv_data