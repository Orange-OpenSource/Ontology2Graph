
''' This script plots line chart from concatenated file. The name of the KPI
must be use as a first argument and the location of the concatenated file 
as a second argument when laucnhing the python script'''

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys

# use argument as constant
Y_NAME = sys.argv[1]
FILE_NAME = sys.argv[2]

df = pd.read_csv((FILE_NAME))

df['date'] = pd.to_datetime(df['date'],format='%Y-%m-%d %H:%M:%S',errors="coerce")
df=df.sort_values(by=['date'])
#df= df.set_index('date')

fig = px.line(df, x='date', y=Y_NAME, markers=True)

fig.update_layout(
    title={
        'text': f'Time Serie {Y_NAME}',
        'font': {
            'size': 24,
            'color': 'blue',
            'family': 'Arial',
            'weight': 'bold'
        },
        'x': 0.5,  # Center the title
        'xanchor': 'center',
        'yanchor': 'top'
    }
)


fig.show()




#fig = go.Figure()
#fig.add_trace(go.Scatter(
#     x=df.index,
#     y=df[Y_NAME],
#     mode='lines+markers'
#     ))

#fig.update_layout(title=
#                  {'text' : f'time serie {Y_NAME}',
#                   'font' : {'size': 24, 'family': 'Arial', 'weight': 'bold'}})
#fig.show()
