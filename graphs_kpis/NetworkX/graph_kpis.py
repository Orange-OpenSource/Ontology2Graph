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
ONTO = os.path.expanduser('~/DIGITAL_TWIN/gengraphllm/ontologies/Noria.ttl')

def remove_pred_obj(expr, graph, predi, obje):
    '''remove predicate and target object of an edge'''
    edges_to_remove = [(u, v) for u, v, attr in graph.edges(data=True)
                         if attr.get(expr) == predi and v == obje]
    return graph.remove_edges_from(edges_to_remove)

def get_last_folder_part(string,sep_char):
    """get last part of a folder string"""
    string_parts=string.split(sep_char)
    last_part=string_parts[len(string_parts)-1]
    return last_part

##retrieve all the Datatype properties listed in the ontologies
index_list=[]
DatatypeP=[]

#retreive index line of datatype properties
with open(f'{ONTO}', 'r',encoding='utf-8') as file:
    for index, line in enumerate(file, start=1):
        if 'DatatypeProperty' in line :
            index_list.append(index-1)
    file.close()

#retreive DatatypeProperties based on index
with open(f'{ONTO}', 'r',encoding='utf-8') as file:
    for index, line in enumerate(file, start=1):
        if index in index_list:
            DatatypeP.append(line.strip())
    file.close()

#clean DatatypeProperties
DatatypeProperty=[]
for dtp in DatatypeP:
    dtp=dtp.replace('noria:',"")
    DatatypeProperty.append(dtp)


#List all the ttl graph files in PATH except folder
all_files = [f.name for f in Path(PATH).iterdir() if f.is_file()]

#rebuild complete file path (folder/file)
for i, file in enumerate(all_files):
    all_files[i]= PATH + file

'''transforms ttl files as graph and remove all the nodes belonging to TBOX'''
for file in all_files :
    file_name=get_last_folder_part(file,'/')

    g = rdflib.Graph()
    g.parse(file, format='turtle')

    DiGraph = nx.DiGraph()
    Graph = nx.Graph()

    for subj, pred, obj in g:
        '''remove useless nodes'''
        last_part_pred=get_last_folder_part(pred,'/')

        if last_part_pred in DatatypeProperty :
            '''remove Datatype properties'''
            remove_pred_obj(pred, Graph, pred ,obj)
            remove_pred_obj(pred, DiGraph, pred ,obj)

        elif ('label'in pred)or('type' in pred)or('inScheme' in pred)or('descrption' in pred):
            '''remove '''
            word=['label','type','inScheme','descrption']
            for x in word :
                if x in pred :
                    remove_pred_obj(x, Graph, pred ,obj)
                    remove_pred_obj(x, DiGraph, pred ,obj)

        else :
            last_part_subj=get_last_folder_part(subj,'/')
            last_part_obj=get_last_folder_part(obj,'/')
            #print('toto')
            Graph.add_edge(str(last_part_subj),str(last_part_obj),label=str(last_part_pred))
            DiGraph.add_edge(str(last_part_subj),str(last_part_obj),label=str(last_part_pred))

    ### Common information for Grap and DiGraph ####

    print(f'Knowledge Graph : {file_name}')
    print('Number of Nodes :',DiGraph.number_of_nodes())
    print('Number of edges :',DiGraph.number_of_edges())
    print("degree_histogram", degree_histogram(DiGraph))

    print('############ Graph KPIs ############')

    print('############ DiGrap KPIs ############')


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
    #for node in DiGraph.nodes() :
    #    print(node)

    #### visualisation ####
    net = Network(height="840px", width="100%", bgcolor="#222222", font_color="white",
                  directed=True,neighborhood_highlight=True)

    # set the physics layout of the network
    net.barnes_hut()
    net.from_nx(DiGraph,)
    #print(net.nodes)
    #net.show_buttons(filter_=['physics'])

    OUTPUTFILE= "mon_graphe_de_test.html"
    net.save_graph(OUTPUTFILE)
    full_path=os.path.abspath(OUTPUTFILE)
    print('full path',full_path)

    webbrowser.open(f'file://///wsl.localhost/Ubuntu-24.04{full_path}',autoraise=True)
    #webbrowser.open(full_path,autoraise=True)
