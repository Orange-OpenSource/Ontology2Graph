'''This python scipt merge several knowledge Graphs in an only one. 
You have to pass as a parameter the folder where are stored the Graphs'''

import sys
import os
from pathlib import Path
from utils import ttl_validator, remove_duplicate_prefix,find_duplicates_nodes
from utils import rename_duplicates_nodes

arg = sys.argv[1:]
PATH= arg[0]

OUTPUT_DIR=f'{PATH}/merged_graph/'
OUTPUT_FILE_TEMP=f'{OUTPUT_DIR}/temp.ttl'
MERGED_FILE=f'{OUTPUT_DIR}/merged_graph.ttl'
PATH_ONTOLOGY='ontologies/Noria.ttl'

#manage duplicate nodes in ttl files
duplicates=find_duplicates_nodes(PATH,PATH_ONTOLOGY)
rename_duplicates_nodes(PATH,duplicates)

#Merge the ttl file
all_graphs = [f.name for f in Path(PATH).iterdir() if f.is_file()]
os.makedirs(f'{OUTPUT_DIR}',exist_ok=True)

# Open the output file in write mode
with open(OUTPUT_FILE_TEMP, 'w', encoding='utf-8') as outfile:
    for filename in all_graphs:
        # Open each input file in read mode
        with open(f'{PATH}/{filename}', 'r', encoding='utf-8') as infile:
            # Read the content and write it to the output file
            content = infile.read()
            outfile.write(content)
            # Optionally, add a separator or newline between files
            outfile.write('\n')  # Adds a newline between files

# create the graph

# list all the classes

SEARCH_STRING='a noria:'
class_unique_list=[]

with open (OUTPUT_FILE_TEMP, 'r', encoding='utf-8') as outfile:
    for line in outfile:
        if SEARCH_STRING in line and line not in class_unique_list :
            class_unique_list.append(line)
    outfile.close()

class_unique_list1 = [item.strip() for item in class_unique_list ]
class_unique_list2 = [item.replace(SEARCH_STRING,'') for item in class_unique_list1]
class_list = [item.replace(' ;','') for item in class_unique_list2]

#print(class_list)

# manage prefix in merged file
remove_duplicate_prefix(OUTPUT_FILE_TEMP,MERGED_FILE)

# validate ttl syntax
ttl_validator(OUTPUT_DIR)
