
''' This script concatenate the transposed file, it must be placed in the same 
directory than the transposed files '''

import os
import pandas as pd

# Define Constant
DIRECTORY=os.path.dirname(os.path.abspath(__file__))
FILE_NAME = 'concatenated_file.csv'
SEARCH_STRING = 'transposed'
CONCATENATED_FILE=DIRECTORY+'concatenate_file.csv'

# Retrieve all files transposed file
matching_files = [file for file in os.listdir(DIRECTORY) if SEARCH_STRING in file]

# initiate the concatenated file and remove the first value of matching file
concatenated_df = pd.read_csv(matching_files[0])
del matching_files[0]

# Concat the matching files
for file in matching_files:
    df = pd.read_csv(file)
    # Append the data to the concatenated DataFrame
    concatenated_df = pd.concat([concatenated_df, df], axis=0,ignore_index=True)

# Write the concatenated DataFrame to a new CSV file
concatenated_df.to_csv(FILE_NAME, index=False)
print(f"CSV files have been concatenated into {FILE_NAME} without additional headers.")
