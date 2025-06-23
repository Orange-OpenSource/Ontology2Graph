
''' This script concatenate the transposed file'''

import os
import pandas as pd

# Define the directory path and the string to search for
directory = '/home/pdooze/DIGITAL_TWIN/GenGraphLLM/results/gpt4.1_10_KG/robot_measurements/measurement/'
search_string = 'transposed'
concatenated_file=directory+'concatenate_file.csv'

# List all files in the directory that contain the search string
matching_files = [file for file in os.listdir(directory) if search_string in file]

concatenated_df = pd.read_csv(matching_files[0])

# concat the matching files
for file in matching_files[1:]:
    df = pd.read_csv(file, header=None, skiprows=1)
    # Append the data to the concatenated DataFrame
    concatenated_df = pd.concat([concatenated_df, df], ignore_index=True)

# Write the concatenated DataFrame to a new CSV file
output_file_path = 'concatenated_file.csv'
concatenated_df.to_csv(output_file_path, index=False)

print(f"CSV files have been concatenated into {output_file_path} without additional headers.")
