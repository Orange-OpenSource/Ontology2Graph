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

for file in all_files :
    file_name=get_last_folder_part(file,'/')

    g = rdflib.Graph()
    g.parse(file, format='turtle')

    DiGraph = nx.DiGraph()
    
    #Populate Networkx Graph
    for subj, pred, obj in g: 
        DiGraph.add_edge(str(subj), str(obj), label=str(pred))
    
    print(DatatypeProperty)
    for edges in DiGraph.edges(data=True):
        print(edges[2]['label'])
        #last_part_label=get_last_folder_part(edges,'/')
        #print(last_part_label)
        #if last_part_label in DatatypeProperty :
        #    print('toggggggggggggggggggggggggggggggggggggggggggto')

    for subj, pred, obj in g:
        labels = {}
        last_part_pred=get_last_folder_part(pred,'/')

        if last_part_pred in DatatypeProperty :
            pass
            #print(subj)
            #print(DiGraph.nodes)
            
                #print(attrs)
                #dtp_node = [node for node, attrs in DiGraph.nodes(data=True) if attrs.get('subj') == subj]
            #print(dtp_node)
            #for node in DiGraph.nodes(data=True):
            #    print(node[0])
            #    LABEL = f"Node {node}\n DataTypeProperties : {last_part_pred} : Value : {obj}"
            #    labels[node[0]] = LABEL
            #    print(LABEL)
            #'''remove Datatype properties'''
            #remove_pred_obj(pred, DiGraph, pred ,obj)
            #print(DiGraph.nodes)
            #print(subj, pred, obj)
            
            #for node, attrs in DiGraph.nodes(data=True):
    #    print(node)
    #    LABEL = f"Node {node}\n Type: {attrs.get('datatype')}\n Value: {attrs.get('value')}"
    #    labels[node] = LABEL

        elif ('label'in pred)or('type' in pred)or('inScheme' in pred)or('descrption' in pred):
            pass 
            #word=['label','type','inScheme','descrption']
            #for x in word :
            #    if x in pred :
            #        remove_pred_obj(x, DiGraph, pred ,obj)

        else :
            last_part_subj=get_last_folder_part(subj,'/')
            last_part_obj=get_last_folder_part(obj,'/')
            #print('toto')
            DiGraph.add_edge(str(last_part_subj),str(last_part_obj),label=str(last_part_pred))

            #print(DiGraph.nodes)
            #print(subj, pred, obj)

    #for node, attrs in DiGraph.nodes(data=True):
    #    print(f"Node {node}: {attrs}")

    #### visualisation ####
    net = Network(height="840px", width="100%", bgcolor="#222222", font_color="white",
                  directed=True,neighborhood_highlight=True)

    # set the physics layout of the network
    net.barnes_hut()

    labels = {}
    #for node, attrs in DiGraph.nodes(data=True):
    #    print(node)
    #    LABEL = f"Node {node}\n Type: {attrs.get('datatype')}\n Value: {attrs.get('value')}"
    #    labels[node] = LABEL

    net.from_nx(DiGraph,)
    #net.show_buttons(filter_=['physics'])

    for node in net.nodes:
        #print(node['id'])
        node_id = node['id']
        if node_id in labels:
            node['label'] = labels[node_id]


    OUTPUTFILE= "mon_graphe_de_test.html"
    net.save_graph(OUTPUTFILE)
    full_path=os.path.abspath(OUTPUTFILE)
    print('full path',full_path)

    webbrowser.open(f'file://///wsl.localhost/Ubuntu-24.04{full_path}',autoraise=True)
    #webbrowser.open(full_path,autoraise=True)
