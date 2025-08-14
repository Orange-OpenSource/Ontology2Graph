'''find duplicates nodes in ttl files, just add the folder where the files
are stored as an argument'''

import sys
import os
from pathlib import Path
from collections import Counter
import networkx as nx
import rdflib
from utils import get_last_folder_part, retreive_datatype_properties

arg = sys.argv[1:]
PATH= arg[0]

#List all the ttl graph files in PATH except folder
all_files = [f.name for f in Path(PATH).iterdir() if f.is_file()]

ONTOLOGY = os.path.expanduser('~/DIGITAL_TWIN/gengraphllm/ontologies/Noria.ttl')
DataTypeProperties=retreive_datatype_properties(ONTOLOGY)

#rebuild complete file path (folder/file)
for i, file in enumerate(all_files):
    all_files[i]= PATH + file

j=0
all_nodes=[]
nodes=[]

for file in all_files :

    g = rdflib.Graph()
    g.parse(file, format="turtle")

    nx_graph = nx.DiGraph()

    for subj, pred, obj in g:
        last_part_pred=get_last_folder_part(pred,'/')

        if ('label' in last_part_pred) or ('type' in last_part_pred) or\
           ('inScheme' in last_part_pred) or ('description' in last_part_pred) or\
           ('comment' in last_part_pred) or last_part_pred in DataTypeProperties:
            pass

        else :
            last_part_subj=get_last_folder_part(subj,'/')
            last_part_obj=get_last_folder_part(obj,'/')
            nx_graph.add_edge(str(last_part_subj),str(last_part_obj),label=str(last_part_pred))

    nodes=list(nx_graph.nodes)
    all_nodes.append(nodes)

#transform list of list into a simple list
all_nodes_list = [item for sublist in all_nodes for item in sublist]

print(all_nodes_list,'\n')

counts=Counter(all_nodes_list)
duplicates=[item for item, count in counts.items() if count > 1]
print(f'DUPLICATES {duplicates},\n')

all_nodes_list_unique = list(set(all_nodes_list))
print(f'NODES OF FINAL GRAPH {all_nodes_list_unique},\n')
