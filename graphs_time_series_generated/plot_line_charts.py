
''' This script plots line chart from concatenated file. The name of the KPI
must be use as a first argument and the location of the concatenated file 
(compelte folder PATH + the file itself as a second argument when laucnhing 
the python script'''

import sys
import plotly.express as px
#import kaleido
#from kaleido import write_fig_sync
import pandas as pd
#import os

#kaleido.get_chrome_sync

# use argument as constant
Y_NAME = sys.argv[1]
PATH_FILE = sys.argv[2]

#Construct the SAVE_PATH to store the result
parts=PATH_FILE.split("/")
PATH=""

for i in range(len(parts)-2) :
    PATH = f'{PATH}/{parts[i+1]}'

SAVE_PATH=f'{PATH}/Charts'

#Load the data and process them
df = pd.read_csv((PATH_FILE))

df['date'] = pd.to_datetime(df['date'],format='%Y-%m-%d %H:%M:%S',errors="coerce")
df=df.sort_values(by=['date'])

fig = px.line(df, x='date', y=Y_NAME, markers=True)

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

#Save file
#if not os.path.exists(SAVE_PATH):
#    os.makedirs(f'{SAVE_PATH}')

#print(f'{SAVE_PATH}/{Y_NAME}.svg')

#kaleido.write_fig_sync(fig, path=f"{SAVE_PATH}/{Y_NAME}.png")

#fig.write_image(f"{SAVE_PATH}/{Y_NAME}.svg")

#Dysplay in firefox
#HTML_FILE=f'{SAVE_PATH}/{Y_NAME}.html'

#firefox_path = webbrowser.get("firefox")
#firefox_path.open('file://' + os.path.realpath(HTML_FILE))
