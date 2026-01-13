'''find duplicates nodes in ttl files, just pass as an argument the folder where the ttl files are 
stored and the path file to the Ontology'''

import sys
from pathlib import Path
from collections import Counter
import networkx as nx
import rdflib
from utils_common.utils import retreive_onto_object

arg = sys.argv[1:]
PATH= arg[0]
ONTOLOGY = arg[1]

#List all the ttl graph files in PATH except folder
all_files = [f.name for f in Path(PATH).iterdir() if f.is_file()]

DataTypeProperties=retreive_onto_object(ONTOLOGY,'DatatypeProperty')

#rebuild complete file path (folder/file)
for i, file in enumerate(all_files):
    all_files[i]= PATH + file

j=0
all_nodes=[]
nodes=[]

### populate graphqs from all ttl files ###
for file in all_files :

    g = rdflib.Graph()
    g.parse(file, format="turtle")

    nx_graph = nx.DiGraph()

    for subj, pred, obj in g:
        last_part_pred=Path(str(pred)).name

        if ('label' in last_part_pred) or ('type' in last_part_pred) or\
           ('inScheme' in last_part_pred) or ('description' in last_part_pred) or\
           ('comment' in last_part_pred) or last_part_pred in DataTypeProperties:
            pass

        else :
            last_part_subj=Path(str(subj)).name
            last_part_obj=Path(str(obj)).name
            nx_graph.add_edge(str(last_part_subj),str(last_part_obj),label=str(last_part_pred))

    nodes=list(nx_graph.nodes)
    all_nodes.append(nodes)

#transform list of list into a simple list
all_nodes_list = [item for sublist in all_nodes for item in sublist]

counts=Counter(all_nodes_list)
duplicates=[item for item, count in counts.items() if count > 1]
print(f'DUPLICATES {duplicates},\n')

all_nodes_list_unique = list(set(all_nodes_list))
