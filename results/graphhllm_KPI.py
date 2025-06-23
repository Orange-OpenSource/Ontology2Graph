import pandas as pd
import matplotlib.pyplot as plt
import sys
from datetime import datetime,date,time


def replace_char_at_index(original_string, index_to_replace, new_character):
    # Replace the character at the specified index
    return original_string[:index_to_replace] + new_character + original_string[index_to_replace+1:]


#date = yyyy_mm_dd_hh-mm-ss
arg = sys.argv[1:]
initial_date = arg[0]

print(initial_date)

date_string = replace_char_at_index(initial_date, 10, ' ')
date_string1 = replace_char_at_index(date_string, 13, ':')
date_string2 = replace_char_at_index(date_string1, 16, ':')

print(date_string2)


# Define the format of the date string
date_format = "%Y-%m-%d %H:%M:%S"

# Convert the string to a datetime object
date = datetime.strptime(date_string2, date_format)

print(date)
print(type(date))


'transposing initila data and concat the result'

# Load the CSV file into a DataFrame
input_file = '/home/pdooze/DIGITAL_TWIN/GenGraphLLM/results/gpt4.1_10_KG/robot_measurements/measurement/Third_graph_'+initial_date+'_gpt-4.1-robot_measurement.csv'  # Replace with your input file path
output_file = '/home/pdooze/DIGITAL_TWIN/GenGraphLLM/results/gpt4.1_10_KG/robot_measurements/measurement/Third_graph_'+initial_date+'_gpt-4.1-robot_measurement_transposed.csv'  # Replace with your desired output file path

# Read the CSV file
df = pd.read_csv(input_file)

del df['metric_type']
df = df.rename(columns={'metric_value':date})

#print(df)i

# Transpose the DataFrame
df_transposed = df.transpose()
print(df_transposed)

# Save the transposed DataFrame to a new CSV file
df_transposed.to_csv(output_file, header=False)

print(f"File transposed and saved as {output_file}")


















# Load the data
#df = pd.read_csv('/home/pdooze/DIGITAL_TWIN/GenGraphLLM/results/correct/Third_graph_gemini-1.5-flash.ttl')

# Supposons que ton fichier CSV a des colonnes nommées 'Date' et 'Valeur'
# Remplace 'Date' et 'Valeur' par les noms de colonnes appropriés de ton fichier CSV
# plt.plot(df['Date'], df['Valeur'])

# Ajouter des titres et des labels
# plt.title('Exemple de Line Chart')
# plt.xlabel('Date')
# plt.ylabel('Valeur')

# Afficher le graphique
#plt.show()
