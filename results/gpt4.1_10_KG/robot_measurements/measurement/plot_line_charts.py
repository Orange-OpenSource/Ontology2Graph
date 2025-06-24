
''' This script plots line chart from concatenated file '''

import matplotlib.pyplot as plt
import pandas as pd
import sys

# Define Constant
FILE_NAME = 'concatenated_file.csv'
Y_NAME = sys.argv[1:]

df = pd.read_csv(FILE_NAME)

df.plot(x='metric',y=Y_NAME)
plt.savefig('mon_graphique.svg', dpi=300)
#plt.show()
