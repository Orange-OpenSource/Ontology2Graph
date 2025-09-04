'''list of function to be used '''

import logging
import webbrowser
import os
from pathlib import Path
from rdflib import URIRef, Literal, Namespace
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
    print(dtproperties)
    return dtproperties

def visu_graph(graph,file,html_folder):
    '''dysplay the graph'''

    net = Network(height="1300px", width="100%", bgcolor="#222222", font_color="white",
                  directed=True)
    net.barnes_hut()
    net.from_nx(graph)
    #net.show_buttons(filter_=['physics'])

    os.makedirs(html_folder,exist_ok=True)

    html_file = f'{html_folder}/{Path(file).stem}.html'
    print('html_file',html_file)

    net.save_graph(html_file)

    #webbrowser.open(f'file://///wsl.localhost/Ubuntu-24.04{html_file}',autoraise=True
    webbrowser.open(html_file,autoraise=True)

def populate_graph(g,graph,digraph,ontology):
    '''remove literal and other expression from the graph in order to keep only the real nodes'''
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

    for subj, pred, obj in g:
        #print(pred)
        last_part_pred=[]
        #last_part_pred=get_last_folder_part(pred,'/')
        last_part_pred=Path(pred).name
        print(last_part_pred)
        print(type(last_part_pred))
        #print(last_part_pred2)
        dtp = retreive_datatype_properties(ontology)
        #print(dtp)
        #print(type(dtp))

        if str(last_part_pred) in dtp:
            print(f'{last_part_pred} in DTP' )


        if (isinstance(subj, URIRef) and isinstance(obj, URIRef)
                                        and (pred != rdf.type)
                                        and (pred != rdfs.isDefinedBy)
                                        and (last_part_pred not in dtp)):

            #print(subj, pred, obj)
            digraph.add_edge(str(subj), str(obj), label=str(pred),color='white')
            digraph.add_node(str(subj),label=str(pred),size=80,color='red')
            digraph.add_node(str(obj),label=str(pred),size=80,color='blue')
            #digraph.add_edge(str(subj),str(obj))
            graph.add_edge(str(subj), str(obj), label=str(pred))

def remove_literal_from_nodes_old(g,graph,digraph,ontology): ##OLD
    '''remove literal and other expression from the graph in order to keep only the nodes'''

    datatypeproperties=retreive_datatype_properties(ontology)

    for subj, pred, obj in g:
        last_part_pred=get_last_folder_part(pred,'/')

        if (('label' in last_part_pred) or ('type' in last_part_pred) or
           ('inScheme' in last_part_pred) or ('description' in last_part_pred) or
           ('comment' in last_part_pred) or last_part_pred in datatypeproperties):
            pass
        else :
            last_part_subj=get_last_folder_part(subj,'/')
            last_part_obj=get_last_folder_part(obj,'/')
            #print({last_part_subj},{last_part_pred},{last_part_obj})
            graph.add_edge(str(last_part_subj),str(last_part_obj),label=str(last_part_pred))
            digraph.add_edge(str(last_part_subj),str(last_part_obj),label=str(last_part_pred))

def log_kpis(file_name,graph,digraph,cumul_nodes):
    '''compute and logs KPIS'''

    logger = logging.getLogger('Graph_KPI')

    logger.info('##################################################')
    logger.info('#### Common information for Graph and DiGraph ####')
    logger.info('Knowledge Graph : %s',file_name)
    logger.info('Number of Nodes : %s',digraph.number_of_nodes())
    logger.info('Number of edges : %s',digraph.number_of_edges())
    cumul_nodes = cumul_nodes + digraph.number_of_nodes()
    logger.info('cumulative number of nodes : %s',cumul_nodes )
    logger.info('degree_histogram : %s', degree_histogram(graph))
    logger.info('number of self loop : %s', number_of_selfloops(graph))

    logger.info('#### Graph KPIs ####')
    logger.info('Graph density : %s',density(graph))

    logger.info('#### DiGrap KPIs ####')
    logger.info('DiGraph density : %s',density(digraph))
    logger.info('Average degree connectivity : %s', average_degree_connectivity(graph))
    logger.info('#### Subject, Object, predicate ####')
    for s, p, data in digraph.edges(data=True):
        logger.info('%s,%s,%s',s,p,data)
    logger.info('#### NODES #### :%s',len(digraph.nodes))
    logger.info('%s',digraph.nodes)
    logger.info('##################################################\n')

    return cumul_nodes

def set_the_graph(file,log_html_folder):
    '''set the graph based on the turtle file and log some infos'''
    digraph = nx.DiGraph()
    graph = nx.Graph()
    g = rdflib.Graph()
    g.parse(f'{file}', format='turtle')

    ### set logger ###
    #directory=Path(file).parent.resolve()
    log_file=f'{Path(log_html_folder)}/URI_and_LITERAL.log'

    logger_file1 = logging.getLogger('URI_and_LITERAL')
    handler_file1 = logging.FileHandler(log_file)
    logger_file1.setLevel(logging.INFO)
    logger_file1.addHandler(handler_file1)

    logger_file1.info('##################################################')
    logger_file1.info('%s',file)
    for s, p, o in g:
        if isinstance(s, URIRef):
            logger_file1.info('URIRef Subject : %s',s)
        if isinstance(o, Literal):
            logger_file1.info('Literal Object : %s',o)
    logger_file1.info('##################################################')

    ### sort and remove duplicate lines ###
    with open(log_file, 'r',encoding='utf-8') as f:
        unique_lines = set(f.readlines())
        f.close()

    sorted_lines=sorted(unique_lines)  # Sorts in alphabetical order

    with open(log_file, 'w',encoding='utf-8') as f:
        f.writelines(sorted_lines)
        f.close()

    return g, digraph, graph #, file_name
