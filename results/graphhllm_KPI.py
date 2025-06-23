import pandas as pd
import matplotlib.pyplot as plt



'transposing initila data and concat the result'

# Load the CSV file into a DataFrame
input_file = '/home/pdooze/DIGITAL_TWIN/GenGraphLLM/results/gpt4.1_10_KG/robot_measurements/measurement/Third_graph_2025-06-16_16-00-02_gpt-4.1-robot_measurement.csv'  # Replace with your input file path
output_file = '/home/pdooze/DIGITAL_TWIN/GenGraphLLM/results/gpt4.1_10_KG/robot_measurements/measurement/Third_graph_2025-06-16_16-00-02_gpt-4.1-robot_measurement_transposed.csv'  # Replace with your desired output file path

# Read the CSV file
df = pd.read_csv(input_file)
del df['metric_type']
print(df)

# Transpose the DataFrame
df_transposed = df.transpose()

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
