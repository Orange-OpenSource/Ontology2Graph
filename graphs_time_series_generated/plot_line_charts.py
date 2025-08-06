
''' This script plots line chart based on KPI's timse series build from robot measurements. The 
name of the KPI must be use as a first argument and the location of the concatenated file 
(compelte folder PATH + the file itself as a second argument when laucnhing the python script'''

import sys
import os
import plotly.express as px
import pandas as pd

# use argument as constant
Y_NAME = sys.argv[1]
PATH_FILE = sys.argv[2]

#Construct the SAVE_PATH to store the result
parts=PATH_FILE.split("/")
PATH=""

for i in range(len(parts)-2) :
    PATH = f'{PATH}/{parts[i+1]}'

SAVE_PATH=f'{PATH}/Charts'

os.makedirs(f'{SAVE_PATH}', exist_ok=True)

#Load the data and process them
df = pd.read_csv((PATH_FILE))

df['date'] = pd.to_datetime(df['date'],format='%Y-%m-%d %H:%M:%S',errors="coerce")
df=df.sort_values(by=['date'])

fig = px.line(df, x='date', y=Y_NAME, markers=True)
#fig = go.Figure(data=go.df,x='date', y=Y_NAME, markers=True )

fig.update_layout(
    title={
        'text': f'Time Serie {Y_NAME}',
        'font': {
            'size': 24,
            'color': 'blue',
            'family': 'Arial'
        },
        'x': 0.5,  # Center the titleS
        'xanchor': 'center',
        'yanchor': 'top'
    }
)

fig.show()
fig.write_html(f'{SAVE_PATH}/{Y_NAME}.html')
