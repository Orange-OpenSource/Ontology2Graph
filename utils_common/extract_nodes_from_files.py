'''extract nodes from files
to be check what is considered a node or not in rdlib graph'''

import sys
from os import getcwd
import csv
from pathlib import Path
import rdflib
import networkx as nx
from utils_common.utils import retreive_datatype_properties
#from utils_common.utils import retreive_object_properties

arg = sys.argv[1:]
file= arg[0]

g = rdflib.Graph()
g.parse(file, format="turtle")

nx_graph = nx.DiGraph()

ONTO='/home/pdooze/DIGITAL_TWIN/gengraphllm/generate_ttl_files/ontologies/Noria.ttl'
datatypeproperties=retreive_datatype_properties(ONTO)
#objectproperties=retreive_object_properties(ONTO)

for subj, pred, obj in g:
    last_part_pred=Path(str(pred)).stem

    if ('label' in last_part_pred) or ('type' in last_part_pred) or\
        ('inScheme' in last_part_pred) or ('description' in last_part_pred) or\
            ('comment' in last_part_pred) or last_part_pred in datatypeproperties:\
                #or last_part_pred in objectproperties:
        pass

    else :
        last_part_subj=Path(str(subj)).name
        last_part_obj=Path(str(obj)).name
        nx_graph.add_edge(str(last_part_subj),str(last_part_obj),label=str(last_part_pred))

nodes=list(nx_graph.nodes)

with open(f'{getcwd()}/nodes.csv', 'w', encoding='utf-8',newline='') as f:
    writer = csv.writer(f)
    for item in nodes:
        writer.writerow([item])
    f.close()
