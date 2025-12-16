'''extract nodes from file'''
''' TO BE CHECK WHAT IS CONSIDERED A NODE OR NOT IN RDFLIB GRAPH'''

from os import getcwd
import sys
import csv
from pathlib import Path
import rdflib
import networkx as nx
from utils_common.utils import get_last_folder_part,retreive_datatype_properties,retreive_object_properties

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
        last_part_subj=get_last_folder_part(subj,'/')
        last_part_obj=get_last_folder_part(obj,'/')
        nx_graph.add_edge(str(last_part_subj),str(last_part_obj),label=str(last_part_pred))

nodes=list(nx_graph.nodes)

with open(f'{getcwd()}/nodes.csv', 'w', encoding='utf-8',newline='') as f:
    writer = csv.writer(f)
    for item in nodes:
        writer.writerow([item])
    f.close()
