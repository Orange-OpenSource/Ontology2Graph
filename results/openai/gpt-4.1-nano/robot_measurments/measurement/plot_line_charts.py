
''' This script plots line chart from concatenated file the name of the KPI
must be use as an argument when laucnhing the python file'''

import matplotlib.pyplot as plt
import pandas as pd
import sys

# Define Constant
FILE_NAME = 'concatenated_file.csv'
Y_NAME = sys.argv[1:]

df = pd.read_csv((FILE_NAME))#,index_col='date',parse_dates=True)
df['date_time'] = pd.to_datetime(df['date'],format='%Y-%m-%d %H:%M:%S',errors="coerce")
df=df.sort_values(by=['date_time'])
df=df.drop('date',axis="columns")
df= df.set_index('date_time')

print(df)

#ligne = df.iloc[1]
# Afficher la valeur dans la colonne 'Nom' pour cette ligne
#print(type(ligne['date']))
#print(type(ligne['date_time']))
#print(df.dtypes)

df.plot(y=Y_NAME)
#plt.savefig(Y_NAME[0], dpi=300)
plt.show()

