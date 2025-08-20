'''list of function to be used '''

import logging
import webbrowser
import os
from pathlib import Path
from pyvis.network import Network
import networkx as nx
from networkx.classes.function import density, degree_histogram, number_of_selfloops
from networkx import average_degree_connectivity
import rdflib

def remove_pred_obj(expr, graph, predi, obje):
    '''remove predicate and target object of an edge'''
    edges_to_remove = [(u, v) for u, v, attr in graph.edges(data=True)
                         if attr.get(expr) == predi and v == obje]
    return graph.remove_edges_from(edges_to_remove)

def get_last_folder_part(string, sep_char):
    """get last part of a folder string"""
    string_parts=string.split(sep_char)
    last_part=string_parts[len(string_parts)-1]
    if last_part=='':
        last_part=string_parts[len(string_parts)-2]
    return last_part

def retreive_datatype_properties(ontology):
    '''create a list of all the data type properties from the ontologie'''

    index_list=[]
    dtprop=[]
    dtproperties=[]

    #build index list of DatatypeProperty
    with open(f'{ontology}', 'r',encoding='utf-8') as file:
        for index, line in enumerate(file, start=1):
            if 'DatatypeProperty' in line :
                index_list.append(index-1)
    file.close()

    #retreive DatatypeProperties based on index list
    with open(f'{ontology}', 'r',encoding='utf-8') as file:
        for index, line in enumerate(file, start=1):
            if index in index_list:
                dtprop.append(line.strip())
                #print(line.strip())
    file.close()

    #clean DatatypeProperties
    for dtp in dtprop:
        dtp=dtp.replace('noria:',"")
        dtproperties.append(dtp)
    return dtproperties

def visu_graph(graph,file):
    '''dysplay the graph'''

    net = Network(height="1300px", width="100%", bgcolor="#222222", font_color="white",
                  directed=True)
    net.barnes_hut()
    net.from_nx(graph)
    #net.show_buttons(filter_=['physics'])

    html_folder= f'{Path(file).parent}/html/'
    os.makedirs(html_folder,exist_ok=True)

    html_file = f'{html_folder}{Path(file).stem}.html'
    print('html_file',html_file)

    net.save_graph(f'{html_file}')

    #webbrowser.open(f'file://///wsl.localhost/Ubuntu-24.04{html_file}',autoraise=True)
    webbrowser.open(html_file,autoraise=True)

def remove_literal_from_nodes(g,graph,digraph,ontology):
    '''remove literal and otrher expression from the graph in order to keep only the nodes'''

    datatypeproperties=retreive_datatype_properties(ontology)

    for subj, pred, obj in g:
        last_part_pred=get_last_folder_part(pred,'/')

        literal_type=['label','type','inScheme','description','comment']

        for lt in literal_type:
            if lt in datatypeproperties:
                pass
            else :
                last_part_subj=get_last_folder_part(subj,'/')
                last_part_obj=get_last_folder_part(obj,'/')
                #print({last_part_subj},{last_part_pred},{last_part_obj})
                graph.add_edge(str(last_part_subj),str(last_part_obj),label=str(last_part_pred))
                digraph.add_edge(str(last_part_subj),str(last_part_obj),label=str(last_part_pred))


def log_kpis(path,file_name,graph,digraph,cumul_nodes):
    '''compute KPIS'''

    logging.basicConfig(level=logging.INFO, filename=f'{path}html/Graphs.log', filemode='w',
                         format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info('#### Common information for Graph and DiGraph ####')
    logging.info('Knowledge Graph : %s',file_name)
    logging.info('Number of Nodes : %s',digraph.number_of_nodes())
    logging.info('Number of edges : %s',digraph.number_of_edges())
    cumul_nodes = cumul_nodes + digraph.number_of_nodes()
    logging.info('cumulative number of nodes : %s',cumul_nodes )
    logging.info('degree_histogram : %s', degree_histogram(graph))
    logging.info('number of self loop : %s', number_of_selfloops(graph))

    logging.info('#### Graph KPIs ####')
    logging.info('Graph density : %s',density(graph))
    #print('number of triangles by nodes',nx.triangles(graph),'\n')

    logging.info('#### DiGrap KPIs ####')
    logging.info('DiGraph density : %s',density(digraph))
    logging.info('Average degree connectivity : %s', average_degree_connectivity(graph))
    logging.info('##################################################\n')

    return cumul_nodes

def set_the_graph(file):
    '''set the graph base on the turtle file'''
    digraph = nx.DiGraph()
    graph = nx.Graph()

    file_name=get_last_folder_part(file,'/')

    g = rdflib.Graph()
    g.parse(f'{file}', format='turtle')

    return g, digraph, graph, file_name
