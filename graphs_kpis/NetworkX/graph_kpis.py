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

def remove_pred_obj(expr, graph):
    '''remove predicate and target object'''
    edges_to_remove = [(u, v) for u, v, attr in graph.edges(data=True)
                         if attr.get(expr) == pred and v == obj]
    return graph.remove_edges_from(edges_to_remove)

##retrieve all the Datatype properties listed in the ontologies
index_list=[]
DatatypeP=[]

#retreive index line of datatype properties
with open(f'{ONTO}', 'r',encoding='utf-8') as file:
    for index, line in enumerate(file, start=1):
        if 'DatatypeProperty' in line :
            #print(f'{index  }:{line.strip()}')
            index_list.append(index-1)
    file.close()

#retreive DatatypeProperties based on index
with open(f'{ONTO}', 'r',encoding='utf-8') as file:
    for index, line in enumerate(file, start=1):
        if index in index_list:
            #print(index,line.strip())
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

    my_subj=[]
    my_pred=[]
    my_obj=[]

    for subj, pred, obj in g:

        #split pred in / / parts
        parts_pred=pred.split("/")
        dtp_pred=parts_pred[len(parts_pred)-1]

        if dtp_pred in DatatypeProperty : #Remove DataTypeProperties

            edges_to_remove = [(u, v) for u, v, attr in Graph.edges(data=True)
            if attr.get(dtp_pred) == pred and v == obj]
            Graph.remove_edges_from(edges_to_remove)

            edges_to_remove = [(u, v) for u, v, attr in DiGraph.edges(data=True)
            if attr.get(dtp_pred) == pred and v == obj]
            DiGraph.remove_edges_from(edges_to_remove)

        # remove useless nodes
        #if 'comment' in pred :
            #remove_pred_obj('comment', Graph)
            #remove_pred_obj('comment', DiGraph)

            #edges_to_remove = [(u, v) for u, v, attr in Graph.edges(data=True)
            #if attr.get('comment') == pred and v == obj]
            #Graph.remove_edges_from(edges_to_remove)

            #edges_to_remove = [(u, v) for u, v, attr in DiGraph.edges(data=True)
            #if attr.get('comment') == pred and v == obj]
            #DiGraph.remove_edges_from(edges_to_remove)

        elif 'label' in pred :
            remove_pred_obj('label', Graph)
            remove_pred_obj('label', DiGraph)

        elif 'type' in pred :
            remove_pred_obj('type', Graph)
            remove_pred_obj('type', DiGraph)

        elif 'license' in pred :
            remove_pred_obj('licence', Graph)
            remove_pred_obj('licence', DiGraph)

        elif 'inScheme' in pred :
            remove_pred_obj('inScheme', Graph)
            remove_pred_obj('inScheme', DiGraph)

        elif 'description' in pred :
            remove_pred_obj('description', Graph)
            remove_pred_obj('description', DiGraph)

        else :
            print(dtp_pred)
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

    #print(list(DiGraph.nodes()))
    print("number of nodes : ", len(DiGraph.nodes()))
    #print(list(DiGraph.edges()))
    print("number of edges : ", len(DiGraph.edges()))
    #print(my_subj)

    #for node in DiGraph.nodes() :
    #    print(node)

    print('\n')

    #### visualisation
    #net=Network(height='840px',width='1700px',select_menu=True,filter_menu=True)
    net = Network(height="840px", width="100%", bgcolor="#222222", font_color="white")

    # set the physics layout of the network
    net.barnes_hut()
    net.from_nx(DiGraph)
    net.show_buttons(filter_=['physics'])

    OUTPUTFILE= "mon_graphe_de_test.html"
    net.save_graph(OUTPUTFILE)
    full_path=os.path.abspath(OUTPUTFILE)
    print('full path',full_path)

    #webbrowser.open(f'file://///wsl.localhost/Ubuntu-24.04{full_path}',autoraise=True)
    webbrowser.open(full_path,autoraise=True)
