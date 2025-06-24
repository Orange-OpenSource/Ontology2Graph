
''' This script plots line chart from concatenated file the name of the KPI
must be use as an argument when laucnhing the python file'''

import matplotlib.pyplot as plt
import pandas as pd
import sys

# Define Constant
FILE_NAME = 'concatenated_file.csv'
Y_NAME = sys.argv[1:]

df = pd.read_csv(FILE_NAME)

df.plot(x='date',y=Y_NAME)
plt.savefig(Y_NAME[0], dpi=300)
plt.show()

