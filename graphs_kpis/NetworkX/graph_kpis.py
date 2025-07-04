''' This python script compute some Knowledge Graphs KPIs. You must pass as an argument the 
location folder where are stored all the ttl files'''

import sys
from pathlib import Path
import networkx as nx
import rdflib
from networkx.algorithms import approximation

arg = sys.argv[1:]
PATH= arg[0]

#List all the files in PATH except folder
all_files = [f.name for f in Path(PATH).iterdir() if f.is_file()]

#rebuild complete file path (folder/file)
for i, file in enumerate(all_files):
    all_files[i]= PATH + file

for file in all_files:

    #retrieve file name
    parts = file.split("/")
    file_name_pos = len(parts)
    file_name = parts[file_name_pos-1]

    #load the knowledge graph in G
    g = rdflib.Graph()
    g.parse(file, format='turtle')

    G = nx.DiGraph()

    for subj, pred, obj in g:
        # Convert RDF nodes to strings for node labels
        SUBJ_STR = str(subj)
        PRED_STR = str(pred)
        OBJ_STR = str(obj)

        # Add nodes (optional, as adding edges will add nodes automatically)
        G.add_node(SUBJ_STR)
        G.add_node(OBJ_STR)

        # Add edge with predicate as label (if desired)
        G.add_edge(SUBJ_STR, OBJ_STR, label=PRED_STR)

    print(f'Knowledge Graph : {file_name}')
    print('Number of Nodes :',G.number_of_nodes())
    print('Number of edges :',G.number_of_edges())
    print('Is the graph is directed ? :',G.is_directed())

    if G.is_directed() is False : #is_connected and components not implemented for directed Graph
        print('Is the graph is connected ? :',nx.is_connected(G))
        print('How many component ? :',nx.number_connected_components(G))

    print('Is the graph is multigraph ? :',G.is_multigraph())
    #print('Is the graph is strongly connected ? :',nx.is_strongly_connected(G))

    #if nx.is_strongly_connected(G) :
    #    print('Diameter :', nx.diameter(G),'\n')
    #else : print('Diameter cannot be compute because the Graph is not strongly connected')

    #print('number of triangles by nodes',nx.triangles(G),'\n')

    print('########### APPROX ################')
    #print('Pairs of nodes connected : ',approximation.all_pairs_node_connectivity(G))
    print('Node connectivity approx',approximation.node_connectivity(G))
    #print('components',approximation.k_components(G))
    #print('maximum independent set',nx.approximation.maximum_indep
    print("degree",G.degree())
    print("in degree",G.in_degree())
    print("out degree",G.out_degree())




    print('\n')
