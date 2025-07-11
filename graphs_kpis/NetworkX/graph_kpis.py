''' This python script compute some Knowledge Graphs KPIs. You must pass as an argument the 
location folder where are stored all the ttl files'''

import sys
import os
from pathlib import Path
import webbrowser
from utils import get_last_folder_part, retreive_datatype_properties
import networkx as nx
from networkx.classes.function import density, degree_histogram, number_of_selfloops
from networkx import average_degree_connectivity
import rdflib
from pyvis.network import Network

arg = sys.argv[1:]
PATH= arg[0]
ONTOLOGY = os.path.expanduser('~/DIGITAL_TWIN/gengraphllm/ontologies/Noria.ttl')

DataTypeProperties=retreive_datatype_properties(ONTOLOGY)

#List all the ttl graph files in PATH except folder
all_files = [f.name for f in Path(PATH).iterdir() if f.is_file()]

#rebuild complete file path (folder/file)
for i, file in enumerate(all_files):
    all_files[i]= PATH + file

for file in all_files :
    file_name=get_last_folder_part(file,'/')

    g = rdflib.Graph()
    g.parse(file, format='turtle')

    DiGraph = nx.DiGraph()
    Graph = nx.Graph()

    for subj, pred, obj in g:
        last_part_pred=get_last_folder_part(pred,'/')

        if (last_part_pred in DataTypeProperties) or\
            ('label'in pred)or('type' in pred)or('inScheme' in pred)or('descrption' in pred):
            pass

        else :
            last_part_subj=get_last_folder_part(subj,'/')
            last_part_obj=get_last_folder_part(obj,'/')
            Graph.add_edge(str(last_part_subj),str(last_part_obj),label=str(last_part_pred))
            DiGraph.add_edge(str(last_part_subj),str(last_part_obj),label=str(last_part_pred))

    ### Common information for Graph and DiGraph ####
    print('\n #### Common information for Graph and DiGraph #### \n')
    print(f'Knowledge Graph : {file_name}')
    print('Number of Nodes :',DiGraph.number_of_nodes())
    print('Number of edges :',DiGraph.number_of_edges())
    print('degree_histogram :', degree_histogram(Graph))
    print('number of self loop :', number_of_selfloops(Graph))

    print('\n #### Graph KPIs #### \n')
    print("Graph density",density(Graph))
    print('number of triangles by nodes',nx.triangles(Graph),'\n')

    print('\n #### DiGrap KPIs #### \n')
    print("DiGraph density",density(DiGraph))
    print("Average degree connectivity", average_degree_connectivity(Graph))
    print('\n')

    #### visualisation ####
    net = Network(height="840px", width="100%", bgcolor="#222222", font_color="white",
                  directed=True,neighborhood_highlight=True)

    # set the physics layout of the network
    net.barnes_hut()
    net.from_nx(DiGraph,)
    #net.show_buttons(filter_=['physics'])

    OUTPUTFILE= "mon_graphe_de_test.html"
    net.save_graph(OUTPUTFILE)
    full_path=os.path.abspath(OUTPUTFILE)
    print('full path',full_path)

    #webbrowser.open(f'file://///wsl.localhost/Ubuntu-24.04{full_path}',autoraise=True)
    #webbrowser.open(full_path,autoraise=True)
