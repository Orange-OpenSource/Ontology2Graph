''' This python script compute some Knowledge Graphs KPIs. You must pass as an argument the 
location folder where are stored all the ttl files'''

import sys
import os
from pathlib import Path
import webbrowser
import networkx as nx
import rdflib
from networkx.classes.function import degree_histogram
from networkx import approximation
from pyvis.network import Network

arg = sys.argv[1:]
PATH= arg[0]
#ONTO='/home/pdooze/DIGITAL_TWIN/gengraphllm/ontologies/Noria.ttl'
ONTO='/home/piod7321/DIGITAL_TWIN/gengraphllm/ontologies/Noria.ttl'

def remove_pred_obj(expr, graph, predi, obje):
    '''remove predicate and target object'''
    edges_to_remove = [(u, v) for u, v, attr in graph.edges(data=True)
                         if attr.get(expr) == predi and v == obje]
    return graph.remove_edges_from(edges_to_remove)

##retrieve all the Datatype properties listed in the ontologies
index_list=[]
DatatypeP=[]

#retreive index line of datatype properties
with open(f'{ONTO}', 'r',encoding='utf-8') as file:
    for index, line in enumerate(file, start=1):
        #print(line)
        if 'DatatypeProperty' in line :
            #print(f'{index  }:{line.strip()}')
            index_list.append(index-1)
    file.close()

#retreive DatatypeProperties based on index
with open(f'{ONTO}', 'r',encoding='utf-8') as file:
    for index, line in enumerate(file, start=1):
        if index in index_list:
            #print(index,line.strip())
            #print(line)
            DatatypeP.append(line.strip())
    file.close()

#clean DatatypeProperties
DatatypeProperty=[]
for dtp in DatatypeP:
    dtp=dtp.replace('noria:',"")
    #print(dtp)
    DatatypeProperty.append(dtp)

#List all the ttl graph files in PATH except folder
all_files = [f.name for f in Path(PATH).iterdir() if f.is_file()]

#rebuild complete file path (folder/file)
for i, file in enumerate(all_files):
    all_files[i]= PATH + file

for file in all_files :

    #retrieve file name
    parts = file.split("/")
    file_name_pos = len(parts)
    file_name = parts[file_name_pos-1]

    #load the knowledge graph in G
    g = rdflib.Graph()
    g.parse(file, format='turtle')

    DiGraph = nx.DiGraph()
    Graph = nx.Graph()

    for subj, pred, obj in g:

        #retrive last part of predicate
        parts_pred=pred.split("/")
        dtp_pred=parts_pred[len(parts_pred)-1]

        if dtp_pred in DatatypeProperty :
            #Remove edge and dtp_pred node'
            remove_pred_obj(dtp_pred, Graph, pred ,obj)
            remove_pred_obj(dtp_pred, DiGraph, pred ,obj)

        elif 'label' in pred :
            remove_pred_obj('label', Graph, pred ,obj)
            remove_pred_obj('label', DiGraph, pred ,obj)

        elif 'type' in pred :
            remove_pred_obj('type', Graph, pred ,obj)
            remove_pred_obj('type', DiGraph, pred ,obj)

        elif 'inScheme' in pred :
            remove_pred_obj('inScheme', Graph, pred ,obj)
            remove_pred_obj('inScheme', DiGraph, pred ,obj)

        elif 'description' in pred :
            remove_pred_obj('description', Graph, pred ,obj)
            remove_pred_obj('description', DiGraph, pred ,obj)

        else :
            Graph.add_edge(str(subj),str(obj),label=str(dtp_pred))
            DiGraph.add_edge(str(subj),str(obj),label=str(dtp_pred))

    print(f'Knowledge Graph : {file_name}')
    print('Number of Nodes :',DiGraph.number_of_nodes())
    print('Number of edges :',DiGraph.number_of_edges())
    print('Is the graph is directed ? :',DiGraph.is_directed())

    #if DiGraph.is_directed() is False : #is_connected and components not implemented for DiGraph
        #print('Is the graph is connected ? :',nx.is_connected(DiGraph))
        #print('How many component ? :',nx.number_connected_components(DiGraph))

    print('Is the graph is multigraph ? :',DiGraph.is_multigraph())
    #print('Is the graph is strongly connected ? :',nx.is_strongly_connected(G))

    #if nx.is_strongly_connected(G) :
    #    print('Diameter :', nx.diameter(G),'\n')
    #else : print('Diameter cannot be compute because the Graph is not strongly connected')

    #print('number of triangles by nodes',nx.triangles(G),'\n')

    print('########### APPROX ################')
    #print('Pairs of nodes connected : ',approximation.all_pairs_node_connectivity(G))
    print('Node connectivity approx',approximation.node_connectivity(DiGraph))
    #print('components',approximation.k_components(G))
    #print('maximum independent set',nx.approximation.maximum_indep

    #print("degree",G.degree())
    #print("in degree",G.in_degree())
    #print("out degree",G.out_degree())

    #print("average node connectivity", average_node_connectivity(Graph))
    print("degree_histogram", degree_histogram(DiGraph))

    #for node in DiGraph.nodes() :
    #    print(node)

    #### visualisation ####
    net = Network(height="840px", width="100%", bgcolor="#222222", font_color="white",
                  directed=True,neighborhood_highlight=True,)

    # set the physics layout of the network
    net.barnes_hut()
    net.from_nx(DiGraph)
    #net.show_buttons(filter_=['physics'])

    OUTPUTFILE= "mon_graphe_de_test.html"
    net.save_graph(OUTPUTFILE)
    full_path=os.path.abspath(OUTPUTFILE)
    print('full path',full_path)

    #webbrowser.open(f'file://///wsl.localhost/Ubuntu-24.04{full_path}',autoraise=True)
    webbrowser.open(full_path,autoraise=True)
