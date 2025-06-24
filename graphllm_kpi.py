
''' This script transfomed data coming from robots measurement as time series and build line chart,
 it take int account one argument corresponding to the date of the robot measurement file in the 
 following format : 2025-06-16_16-00-02'''

import sys
from datetime import datetime,date
import pandas as pd
import matplotlib.pyplot as plt

#MODEL="vertex_ai/gemini-2.0-flash"
#MODEL='openai/gpt-4.1-mini'
#MODEL='vertex_ai/claude3.7-sonnet'
#MODEL='openai/o1-preview'
#MODEL='openai/o3'
MODEL='openai/gpt-4.1-nano'
#MODEL='openai/gpt-4.1'
#MODEL='vertex_ai/gemini-1.5-flash'
#MODEL='openai/o4-mini'
#MODEL='openai/gpt-4o'
#MODEL='vertex_ai/gemini-1.5'
#MODEL="openai/gpt-4o-mini"
#MODEL="openai/o3-mini"
#MODEL="vertex_ai/claude3.5-sonnet-v2"
#MODEL="openai/o1"
#MODEL="vertex_ai/codestral" #no answer
#MODEL="openai/o1-mini"
#MODEL="openai/gpt-3.5-turbo"

arg = sys.argv[1:]
initial_date = arg[0]

# Define the format of the date string
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
PATH=f'/home/pdooze/DIGITAL_TWIN/GenGraphLLM/results/{MODEL}/robot_measurements/measurement/Third_graph_'

def replace_char_at_index(original_string, index_to_replace, new_character):
    '''replacement of characters that doesn't conform to the date format'''
    return original_string[:index_to_replace] + new_character + original_string[index_to_replace+1:]

date_string = replace_char_at_index(initial_date, 10, ' ')
date_string1 = replace_char_at_index(date_string, 13, ':')
date_string2 = replace_char_at_index(date_string1, 16, ':')

# Convert the string to a datetime object
date = datetime.strptime(date_string2, DATE_FORMAT)

'transposing initial data and concat the result'

# Load the CSV file into a DataFrame
input_file = PATH+initial_date+'_gpt-4.1-robot_measurement.csv'
output_file = PATH+initial_date+'_gpt-4.1-robot_measurement_transposed.csv'

# Read the CSV file
df = pd.read_csv(input_file)

# remove & rename columns and KPIs
del df['metric_type']
df = df.rename(columns={'metric_value':date})
df = df.rename(columns={'metric':'date'})

# Transpose the DataFrame
df_transposed = df.transpose()
print(df_transposed)

# Save the transposed DataFrame to a new CSV file
df_transposed.to_csv(output_file, header=False)

print(f"File transposed and saved as {output_file}")

