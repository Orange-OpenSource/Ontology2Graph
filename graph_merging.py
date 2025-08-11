'''This python scipt merge several knowledge Graph in an only one. 
You have to pass as a parameter the folder where are stored the graphs'''

#/home/pdooze/DIGITAL_TWIN/gengraphllm/results/graphs_time_series_generated/vertex_ai/gemini-2.0-flash/outside_test

import sys
import os
from pathlib import Path
import networkx as nx


arg = sys.argv[1:]
PATH= arg[0]

all_graphs = [f.name for f in Path(PATH).iterdir() if f.is_file()]
#print(all_graphs)

OUTPUT_DIR=f'{PATH}/merged_graphs'
os.makedirs(f'{OUTPUT_DIR}',exist_ok=True)
OUTPUT_FILE=f'{OUTPUT_DIR}/merged_graph.ttl'

# Open the output file in write mode
with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
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

with open (OUTPUT_FILE, 'r', encoding='utf-8') as outfile:
    for line in outfile:
        if SEARCH_STRING in line and line not in class_unique_list :
            class_unique_list.append(line)
    outfile.close()

class_unique_list1 = [item.strip() for item in class_unique_list ]
class_unique_list2 = [item.replace(SEARCH_STRING,'') for item in class_unique_list1]
class_list = [item.replace(' ;','') for item in class_unique_list2]

print(class_list)

# List all the predicate

# List all the nodes by classes

# manage prefix

filtered_lines=[]
prefix_lines=[]

with open (OUTPUT_FILE, 'r', encoding='utf-8') as outfile:
    lines = outfile.readlines()
    prefix_lines = [lines for lines in lines if lines.startswith('@')]
    nodes_lines= [lines for lines in lines if not lines.startswith('@')]
    outfile.close()

prefix_lines_unique=[]

#remove duplicate prefix
for item in prefix_lines:
    if item not in prefix_lines_unique:
        prefix_lines_unique.append(item)

#Need to remove duplicate nodes

with open ('Graph.ttl', 'w', encoding='utf-8') as graph:
    graph.writelines(prefix_lines_unique)
    graph.writelines(filtered_lines)
    graph.close()
