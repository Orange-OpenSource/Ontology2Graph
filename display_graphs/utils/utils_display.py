# Software Name : Ontologie2Graph
# SPDX-FileCopyrightText: Copyright (c) Orange SA
# SPDX-License-Identifier: BSD-4-Clause
#
# This software is distributed under the BSD 4-Clause "Original" or "Old" License,
# see the "LICENSE" file for more details or <license-url

''' Utilities for displaying and visualizing RDF/ontology graphs.

This module provides comprehensive functionality for converting RDF graphs and ontologies
into interactive HTML visualizations using NetworkX and pyvis. It supports both basic
and advanced visualization modes with different levels of customization and node 
categorization.

Main Features:
- Graph preparation and preprocessing for visualization
- HTML folder creation and management
- Interactive network visualization with pyvis
- Node categorization by type (TroubleTicket, ChangeRequest, Application, etc.)
- KPI calculation and logging (node count, density, degree distribution)
- Graph filtering and cleanup (literal removal, predicate/object filtering)
- Ontology object extraction and analysis

Functions:
- create_new_log_html_folder: Creates clean log/HTML output directories
- visu_graph_advanced: Advanced graph visualization with enhanced styling and categorization
- visu_graph_basic: Basic graph visualization with minimal styling
- prepare_graph_to_display_advanced: Prepares graphs for advanced visualization mode
- prepare_graph_to_display_basic: Prepares graphs for basic visualization mode
- log_kpis_advanced/basic: Logs graph metrics and key performance indicators
- retreive_onto_object: Extracts ontology objects by type from RDF files

The module is designed to work with RDF graphs in Turtle (.ttl) format and creates
interactive HTML visualizations that can be opened in web browsers for exploration
and analysis of ontological structures.'''

import logging
import os
import shutil
from pathlib import Path
from rdflib import URIRef, Literal, Namespace,BNode
import networkx as nx
from networkx.classes.function import density, degree_histogram, number_of_selfloops
from networkx import average_degree_connectivity
import rdflib
from utils_common import utils as utils_common

def create_new_log_html_folder(path):
    '''    Create a new log_html folder for storing HTML visualization outputs and logs.
    
    This function creates a fresh log_html directory, removing any existing one to ensure
    clean output generation. The folder location depends on whether the input path is a
    file or directory.
    
    Args:
        path (str or Path): Path to either a file or directory. If it's a file, the log_html 
                            folder will be created in the parent directory. If it's a directory,
                            the log_html folder will be created within that directory.
    
    Returns:
        Path: Path object pointing to the newly created log_html folder.
    
    Behavior:
        - If log_html folder already exists, it will be completely removed first
        - Creates a new empty log_html directory
        - Handles both file and directory inputs appropriately
    
    Example:
        >>> folder = create_new_log_html_folder("/path/to/ontology.ttl")
        >>> # Creates /path/to/log_html/
        
        >>> folder = create_new_log_html_folder("/path/to/directory")
        >>> # Creates /path/to/directory/log_html/'''

    if Path(path).is_file():
        log_html_folder = Path(f'{str(Path(path).parent)}/log_html/')
    else:
        log_html_folder = Path(f'{str(Path(path))}/log_html/')

    if log_html_folder.exists() and log_html_folder.is_dir():
        shutil.rmtree(log_html_folder)

    Path.mkdir(log_html_folder)

    return log_html_folder

def prepare_graph_to_display(file, log_html_folder, ontology, mode):
    ''' Prepare a graph for display by processing RDF data with either basic or advanced mode.
    
    This function merges the functionality of prepare_graph_to_display_advanced and 
    prepare_graph_to_display_basic, allowing selection between basic and advanced 
    processing modes. It parses RDF data, creates NetworkX graphs, handles logging,
    and returns appropriate data structures based on the selected mode.
    
    Args:
        file (str or Path): Path to the RDF/turtle file to process
        log_html_folder (str or Path): Directory for log files and HTML output
        ontology (str or Path): Path to the ontology file for retrieving datatype properties
        mode (str): Processing mode, either "basic" or "advanced"
                   - "basic": Simple graph creation with entity-to-entity relationships only
                   - "advanced": Enhanced processing with node categorization and literal handling
    
    Returns:
        - If mode="basic": returns NetworkX DiGraph
        - If mode="advanced": returns tuple (NetworkX DiGraph, node_type_lists)
            where node_type_lists contains 6 lists of categorized nodes:
            [trouble_ticket_nodes, change_request_nodes, application_nodes,
             network_resource_nodes, network_interface_nodes, network_link_nodes]
    
    Features:
        - RDF parsing and NetworkX graph creation
        - Logging of URIRefs, literals, and blank nodes
        - Exclusion of system predicates (rdf:type, skos:inScheme, rdfs:isDefinedBy)
        - Datatype property filtering
        - Log file sorting and deduplication
        
    Advanced Mode Additional Features:
        - Node categorization by type (TroubleTicket, ChangeRequest, etc.)
        - Entity-to-literal relationship handling
        - Enhanced edge type classification
        - Extended blank node processing
    
    Raises:
        ValueError: If mode is not "basic" or "advanced"
    
    Example:
        >>> # Basic mode
        >>> graph = prepare_graph_to_display("data.ttl", "logs/", "onto.ttl", "basic")
        
        >>> # Advanced mode  
        >>> graph,node_lists=prepare_graph_to_display("data.ttl","logs/","onto.ttl","advanced")'''

    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    skos = Namespace("http://www.w3.org/2004/02/skos/core#")

    ### Initialize node type sets (always initialize to avoid unbound variable errors) ###
    trouble_ticket_nodes = set()
    change_request_nodes = set()
    application_nodes = set()
    network_resource_nodes = set()
    network_interface_nodes = set()
    network_link_nodes = set()

    ### set logger ###
    log_file = f'{Path(log_html_folder)}/URI_and_LITERAL.log'
    log_file_sorted = f'{Path(log_html_folder)}/URI_and_LITERAL_sorted.log'

    logger_file1 = logging.getLogger('URI_and_LITERAL')
    handler_file1 = logging.FileHandler(log_file)
    logger_file1.setLevel(logging.INFO)
    logger_file1.addHandler(handler_file1)

    ### set the graph based on the turtle file and log some infos ###
    digraph = nx.DiGraph()
    g = rdflib.Graph()
    g.parse(f'{file}', format='turtle')

    logger_file1.info('##################################################')
    logger_file1.info('%s', file)

    dtp = utils_common.retreive_onto_object(ontology, "DatatypeProperty")

    ### populate graph with nodes and relations ###
    for subj, pred, obj in g:
        short_pred = Path(str(pred)).name
        if '#' in short_pred:
            short_pred = short_pred.split('#', 1)[1]
        short_subj = Path(str(subj)).name

        ### Advanced mode: Node categorization by type ###
        if mode == "advanced" and short_pred == "type":
            obj_type = Path(str(obj)).name
            if obj_type == "TroubleTicket":
                trouble_ticket_nodes.add(str(short_subj))
            elif obj_type == "ChangeRequest":
                change_request_nodes.add(str(short_subj))
            elif obj_type == "Application":
                application_nodes.add(str(short_subj))
            elif obj_type == "Resource":
                network_resource_nodes.add(str(short_subj))
            elif obj_type == "NetworkInterface":
                network_interface_nodes.add(str(short_subj))
            elif obj_type == "NetworkLink":
                network_link_nodes.add(str(short_subj))

        ### Entity-to-entity relationships ###
        if (
            isinstance(subj, URIRef)
            and isinstance(obj, URIRef)
            and (pred != rdf.type)
            and (pred != skos.inScheme)
            and (pred != rdfs.isDefinedBy)
            and (short_pred not in dtp)
        ):
            short_obj = Path(obj).name
            if mode == "advanced":
                digraph.add_edge(
                    str(short_subj),
                    str(short_obj),
                    label=str(short_pred),
                    edge_type='entity_to_entity',
                )
            else:
                digraph.add_edge(
                    str(short_subj),
                    str(short_obj),
                    label=str(short_pred),
                    color='white'
                )
            logger_file1.info('URIRef Subject : %s', subj)

        ### Entity-to-literal relationships (only in advanced mode) ###
        if (
            mode == "advanced"
            and isinstance(subj, URIRef)
            and isinstance(obj, Literal)
            and (pred != rdf.type)
            and (pred != skos.inScheme)
            and (pred != rdfs.isDefinedBy)
        ):
            ### Create a label for the literal value (truncate if too long) ###
            literal_str = str(obj)[:50] + ('...' if len(str(obj)) > 50 else '')
            literal_node = f"{literal_str}"
            digraph.add_edge(
                str(short_subj),
                literal_node,
                label=str(short_pred),
                edge_type='entity_to_literal',
            )
            logger_file1.info('Literal Object : %s', obj)

        ### Blank nodes ###
        if isinstance(subj, BNode) and (pred != rdf.type) and (pred != skos.inScheme):
            logger_file1.info('Blank Node Subject :%s', subj)
            for subjbn, predbn in g.subject_predicates(subj):
                short_subjbn = Path(str(subjbn)).name
                short_predbn = Path(str(predbn)).name
                if isinstance(obj, URIRef):
                    short_obj = Path(obj).name
                    if mode == "advanced":
                        digraph.add_edge(
                            str(short_subjbn),
                            str(short_obj),
                            label=str(short_predbn),
                            edge_type='entity_to_entity',
                        )
                    else:  ### basic mode ###
                        digraph.add_edge(
                            short_subjbn,
                            short_obj,
                            label=short_predbn,
                            color='white'
                        )
                elif mode == "advanced" and isinstance(obj, Literal):
                    literal_str = str(obj)[:50] + ('...' if len(str(obj)) > 50 else '')
                    digraph.add_edge(
                        str(short_subjbn),
                        literal_str,
                        label=str(short_predbn),
                        edge_type='entity_to_literal',
                    )
                logger_file1.info(
                    'Blank Node Subject :%s,Predicate :%s,Object : %s',
                    short_subjbn,
                    short_predbn,
                    obj,
                )

        ### Log literals in basic mode (without adding to graph) ###
        if mode == "basic" and isinstance(obj, Literal):
            logger_file1.info('Literal Object : %s', obj)

    ### log nodes and Literals ###
    logger_file1.info('##################################################')
    logger_file1.info('%s', file)
    for s, p, o in g:
        if isinstance(s, URIRef):
            logger_file1.info('URIRef Subject : %s', s)
        if isinstance(o, Literal):
            logger_file1.info('Literal Object : %s', o)
        if isinstance(s, BNode):
            logger_file1.info('BNode Subject : %s', s)
    logger_file1.info('##################################################')

    ### sort and remove duplicate lines ###
    with open(log_file, 'r', encoding='utf-8') as log:
        unique_lines = set(log.readlines())
        log.close()

    sorted_lines = sorted(unique_lines)  ### sort in alphabetical order ##
    os.remove(log_file)

    with open(log_file_sorted, 'a', encoding='utf-8') as log_sorted:
        log_sorted.writelines(sorted_lines)
        log_sorted.close()

    node_type_lists = [
            list(trouble_ticket_nodes), list(change_request_nodes),
            list(application_nodes), list(network_resource_nodes),
            list(network_interface_nodes), list(network_link_nodes)]

    return digraph, node_type_lists

def log_kpis(file_name, digraph, cumul_nodes, cumul_density, mode, node_type_lists=None):
    ''' Compute and log Key Performance Indicators (KPIs) for a knowledge graph with mode selection.
    
    This function merges the functionality of log_kpis_advanced and log_kpis_basic,
    allowing selection between basic and advanced logging modes. It calculates graph
    metrics and logs detailed information based on the specified mode.
    
    Args:
        file_name (str): Name of the knowledge graph file being analyzed
        digraph (networkx.DiGraph): The directed graph to analyze
        cumul_nodes (int): Current cumulative count of nodes across multiple graphs
        cumul_density (float): Current cumulative density across multiple graphs
        mode (str): Logging mode, either "basic" or "advanced"
        node_type_lists (list, optional): Required for advanced mode. List containing
        6 sublists of categorized nodes: [trouble_ticket_nodes, change_request_nodes,
        application_nodes, network_resource_nodes, network_interface_nodes, network_link_nodes]
    
    Returns:
        tuple: (updated_cumul_nodes, updated_cumul_density)
            - updated_cumul_nodes (int): New cumulative node count
            - updated_cumul_density (float): New cumulative density
    
    Logged Metrics (All Modes):
        - Knowledge graph filename
        - Total number of nodes and edges
        - Cumulative node count across graphs
        - Degree histogram distribution
        - Number of self-loops
        - Graph density (current and cumulative)
        - Average degree connectivity
        - All edges with subject, predicate, object data
        - Complete node list
        
    Additional Advanced Mode Metrics:
        - Node type categorization (trouble tickets, change requests, etc.)
        - Detailed breakdown by node categories
    
    Raises:
        ValueError: If mode is not "basic" or "advanced"
        ValueError: If mode is "advanced" but node_type_lists is None
    
    Example:
        >>> # Basic mode
        >>> cumul_n, cumul_d = log_kpis("graph.ttl", my_graph, 50, 0.3, "basic")
        
        >>> # Advanced mode
        >>> node_lists = [tt_nodes, cr_nodes, app_nodes, nr_nodes, ni_nodes, nl_nodes]
        >>> cumul_n, cumul_d = log_kpis("graph.ttl", my_graph, 50, 0.3, "advanced", node_lists)'''

    if mode not in ["basic", "advanced"]:
        raise ValueError("Mode must be either 'basic' or 'advanced'")

    if mode == "advanced" and node_type_lists is None:
        raise ValueError("node_type_lists is required for advanced mode")

    logger = logging.getLogger('graph_kpi')

    ### Common logging for both modes ###
    logger.info('##################################################')
    logger.info('Knowledge Graph : %s', file_name)
    logger.info('Number of Nodes : %s', digraph.number_of_nodes())
    logger.info('Number of edges : %s', digraph.number_of_edges())
    cumul_nodes = cumul_nodes + digraph.number_of_nodes()
    logger.info('cumulative number of nodes : %s', cumul_nodes)
    logger.info('degree_histogram : %s', degree_histogram(digraph))
    logger.info('number of self loop : %s', number_of_selfloops(digraph))
    logger.info('####  KPIs ####')
    logger.info('DiGraph density : %s', density(digraph))
    cumul_density = cumul_density + density(digraph)
    logger.info('cumulative density : %s', cumul_density)
    logger.info('Average degree connectivity : %s', average_degree_connectivity(digraph))
    logger.info('#### Subject, Object, predicate ####')
    for s, p, data in digraph.edges(data=True):
        logger.info('%s,%s,%s', s, p, data)
    logger.info('#### NODES #### :%s', len(digraph.nodes))
    logger.info('%s', digraph.nodes)

    ### Advanced mode: additional node type categorization logging ###
    if mode == "advanced" and node_type_lists is not None:
        (trouble_ticket_nodes, change_request_nodes, application_nodes,
         network_resource_nodes, network_interface_nodes, network_link_nodes) = node_type_lists

        logger.info('trouble tickets nodes :%s', trouble_ticket_nodes)
        logger.info('change request nodes :%s', change_request_nodes)
        logger.info('application nodes :%s', application_nodes)
        logger.info('network resource nodes :%s', network_resource_nodes)
        logger.info('network interface nodes :%s', network_interface_nodes)
        logger.info('network link nodes :%s', network_link_nodes)

    logger.info('##################################################\n')

    return cumul_nodes, cumul_density

### old code below for reference ###

def remove_literal_from_nodes_old(g,graph,digraph,ontology):
    '''remove literal and other expression from the graph in order to keep only the nodes

    datatypeproperties=utils_common.retreive_onto_object(ontology,"DatatypeProperty")

    for subj, pred, obj in g:
        last_part_pred=get_last_folder_part(pred,'/')

        if (('label' in last_part_pred) or ('type' in last_part_pred) or
           ('inScheme' in last_part_pred) or ('description' in last_part_pred) or
           ('comment' in last_part_pred) or last_part_pred in datatypeproperties):
            pass
        else :
            last_part_subj=get_last_folder_part(subj,'/')
            last_part_obj=get_last_folder_part(obj,'/')
            graph.add_edge(str(last_part_subj),str(last_part_obj),label=str(last_part_pred))
            digraph.add_edge(str(last_part_subj),str(last_part_obj),label=str(last_part_pred))'''

def remove_pred_obj(expr, graph, predi, obje):
    '''remove predicate and target object of an edge
    edges_to_remove = [(u, v) for u, v, attr in graph.edges(data=True)
                         if attr.get(expr) == predi and v == obje]
    return graph.remove_edges_from(edges_to_remove)'''

def get_last_folder_part(string, sep_char):
    """get last part of a folder string
    string_parts=string.split(sep_char)
    last_part=string_parts[len(string_parts)-1]
    if last_part=='':
        last_part=string_parts[len(string_parts)-2]
    return last_part"""

def retreive_onto_object(ontology,object_type):

    '''create a list of all the object declares in the ontology
    object_type can be DatatypeProperty, ObjectProperty or Class

    index_list=[]
    objects=[]
    object_clean=[]

    #build index list of Object
    with open(f'{ontology}', 'r',encoding='utf-8') as file:
        for index, line in enumerate(file, start=1):
            if f":{object_type} " in line :
                index_list.append(index-1)
    file.close()

    #retrieve Object based on index list
    with open(f'{ontology}', 'r',encoding='utf-8') as file:
        for index, line in enumerate(file, start=1):
            if index in index_list:
                objects.append(line.strip())
    file.close()

    #clean Object
    for obj in objects:
        obj=obj.replace('noria:',"")
        object_clean.append(obj)
    return object_clean'''

def prepare_graph_to_display_basic(file,log_html_folder,ontology):
    """set the graph and remove literal and other expression from the graph in order to keep only
    the real nodes and their relation to display, log some inforations

    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    skos = Namespace("http://www.w3.org/2004/02/skos/core#")

    ### set logger ###
    log_file=f'{Path(log_html_folder)}/URI_and_LITERAL.log'
    log_file_sorted=f'{Path(log_html_folder)}/URI_and_LITERAL_sorted.log'

    logger_file1 = logging.getLogger('URI_and_LITERAL')
    handler_file1 = logging.FileHandler(log_file)
    logger_file1.setLevel(logging.INFO)
    logger_file1.addHandler(handler_file1)

    ### set the graph based on the turtle file and log some infos ###
    digraph = nx.DiGraph()
    g = rdflib.Graph()
    g.parse(f'{file}', format='turtle')

    logger_file1.info('##################################################')
    logger_file1.info('%s',file)

    ### populate graph with nodes and relations only ###
    for subj, pred, obj in g:

        short_pred=Path(str(pred)).name
        short_subj=Path(str(subj)).name
        short_obj=Path(str(obj)).name
        #dtp = utils_common.retreive_datatype_properties(ontology)
        dtp = utils_common.retreive_onto_object(ontology,"DatatypeProperty")

        if (isinstance(subj, URIRef) and isinstance(obj, URIRef) and (pred != rdf.type) and\
            (pred != skos.inScheme) and (pred != rdfs.isDefinedBy) and\
                (short_pred not in dtp)):
            digraph.add_edge(str(short_subj), str(short_obj), label=str(short_pred),color='white')
            logger_file1.info('URIRef Subject : %s',subj)

        if isinstance(obj, Literal):
            logger_file1.info('Literal Object : %s',obj)

        if isinstance(subj, BNode) and (pred != rdf.type) and (pred != skos.inScheme):
            logger_file1.info('Blank Node Subject :%s',subj)
            for subjbn, predbn in g.subject_predicates(subj):
                short_subjbn=Path(str(subjbn)).name
                short_predbn=Path(str(predbn)).name
                digraph.add_edge(short_subjbn,short_obj,label=short_predbn,\
                    color='white')
                logger_file1.info('Blank Node Subject :%s,Predicate :%s,Object : %s',short_subjbn,\
                    short_predbn,short_obj)

    ### log nodes and Literals ###
    logger_file1.info('##################################################')
    logger_file1.info('%s',file)
    for s, p, o in g:
        if isinstance(s, URIRef):
            logger_file1.info('URIRef Subject : %s',s)
        if isinstance(o, Literal):
            logger_file1.info('Literal Object : %s',o)
        if isinstance(s,BNode):
            logger_file1.info('BNode Subject : %s',s)
    logger_file1.info('##################################################')

    ## sort and remove duplicate lines ##
    with open(log_file, 'r',encoding='utf-8') as log:
        unique_lines = set(log.readlines())
        log.close()

    sorted_lines=sorted(unique_lines)  # sort in alphabetical order
    os.remove(log_file)

    with open(log_file_sorted, 'a',encoding='utf-8') as log_sorted:
        log_sorted.writelines(sorted_lines)
        log_sorted.close()

    return digraph"""

def prepare_graph_to_display_advanced(file, log_html_folder, ontology):
    """set the graph and remove literal and other expression from the graph in order to keep only
    the real nodes and their relation to display, log some inforations

    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    skos = Namespace("http://www.w3.org/2004/02/skos/core#")
    #noria = Namespace("http://www.semanticweb.org/noria#")

    trouble_ticket_nodes = set()
    change_request_nodes = set()
    application_nodes = set()
    network_resource_nodes = set()
    network_interface_nodes = set()
    network_link_nodes = set()

    ### set logger ###
    log_file = f'{Path(log_html_folder)}/URI_and_LITERAL.log'
    log_file_sorted = f'{Path(log_html_folder)}/URI_and_LITERAL_sorted.log'

    logger_file1 = logging.getLogger('URI_and_LITERAL')
    handler_file1 = logging.FileHandler(log_file)
    logger_file1.setLevel(logging.INFO)
    logger_file1.addHandler(handler_file1)

    ### set the graph based on the turtle file and log some infos ###
    digraph = nx.DiGraph()
    g = rdflib.Graph()
    g.parse(f'{file}', format='turtle')

    logger_file1.info('##################################################')
    logger_file1.info('%s',file)

    dtp = utils_common.retreive_onto_object(ontology,"DatatypeProperty")

    ### populate graph with nodes and relations (including literals) ###
    for subj, pred, obj in g:

        #subj=str(subject)
        #obj=str(object)
       # pred=str(predicate)

        short_pred=Path(str(pred)).name
        if '#' in short_pred:
            short_pred=short_pred.split('#',1)[1]
        short_subj=Path(str(subj)).name

        # Retrieve nodes by their type to be used in the UI menu for filtering
        if short_pred == "type":
            if Path(str(obj)).name == "TroubleTicket": # Identify TroubleTicket nodes
                trouble_ticket_nodes.add(str(short_subj))

            if Path(str(obj)).name == "ChangeRequest": # Identify ChangeRequest nodes
                change_request_nodes.add(str(short_subj))

            if Path(str(obj)).name == "Application": # Identify Application nodes
                application_nodes.add(str(short_subj))

            if Path(str(obj)).name == "Resource": # Identify NetworkResource nodes
                network_resource_nodes.add(str(short_subj))

            if Path(str(obj)).name == "NetworkInterface": # Identify NetworkInterface nodes
                network_interface_nodes.add(str(short_subj))

            if Path(str(obj)).name == "NetworkLink": # Identify NetworkLink nodes
                network_link_nodes.add(str(short_subj))

        # Entity-to-entity relationships
        if (
            isinstance(subj, URIRef)
            and isinstance(obj, URIRef)
            and (pred != rdf.type)
            and (pred != skos.inScheme)
            and (pred != rdfs.isDefinedBy)
            and (short_pred not in dtp)
        ):
            short_obj = Path(obj).name
            digraph.add_edge(
                str(short_subj),
                str(short_obj),
                label=str(short_pred),
                edge_type='entity_to_entity',
            )
            logger_file1.info('URIRef Subject : %s', subj)

        # Entity-to-literal relationships (datatype properties)
        if (
            isinstance(subj, URIRef)
            and isinstance(obj, Literal)
            and (pred != rdf.type)
            and (pred != skos.inScheme)
            and (pred != rdfs.isDefinedBy)
        ):
            # Create a label for the literal value (truncate if too long)
            literal_str = str(obj)[:50] + ('...' if len(str(obj)) > 50 else '')
            literal_node = f"{literal_str}"
            digraph.add_edge(
                str(short_subj),
                literal_node,
                label=str(short_pred),
                edge_type='entity_to_literal',
            )
            logger_file1.info('Literal Object : %s', obj)

        # Blank nodes
        if (
            isinstance(subj, BNode)
            and (pred != rdf.type)
            and (pred != skos.inScheme)
        ):
            logger_file1.info('Blank Node Subject :%s', subj)
            for subjbn, predbn in g.subject_predicates(subj):
                short_subjbn = Path(str(subjbn)).name
                short_predbn = Path(str(predbn)).name
                if isinstance(obj, URIRef):
                    short_obj = Path(obj).name
                    digraph.add_edge(
                        str(short_subjbn),
                        str(short_obj),
                        label=str(short_predbn),
                        edge_type='entity_to_entity',
                    )
                elif isinstance(obj, Literal):
                    literal_str = str(obj)[:50] + ('...' if len(str(obj)) > 50 else '')
                    digraph.add_edge(
                        str(short_subjbn),
                        literal_str,
                        label=str(short_predbn),
                        edge_type='entity_to_literal',
                    )
                logger_file1.info(
                    'Blank Node Subject :%s,Predicate :%s,Object : %s',
                    short_subjbn,
                    short_predbn,
                    obj,
                )

   ### log nodes and Literals ###
    logger_file1.info('##################################################')
    logger_file1.info('%s',file)
    for s, p, o in g:
        if isinstance(s, URIRef):
            logger_file1.info('URIRef Subject : %s',s)
        if isinstance(o, Literal):
            logger_file1.info('Literal Object : %s',o)
        if isinstance(s,BNode):
            logger_file1.info('BNode Subject : %s',s)
    logger_file1.info('##################################################')

    ## sort and remove duplicate lines ##
    with open(log_file, 'r',encoding='utf-8') as log:
        unique_lines = set(log.readlines())
        log.close()

    sorted_lines=sorted(unique_lines)  # sort in alphabetical order
    os.remove(log_file)

    with open(log_file_sorted, 'a',encoding='utf-8') as log_sorted:
        log_sorted.writelines(sorted_lines)
        log_sorted.close()

    node_type_lists = [list(trouble_ticket_nodes), list(change_request_nodes),\
                        list(application_nodes), list(network_resource_nodes),\
                            list(network_interface_nodes), list(network_link_nodes)]
    return digraph, node_type_lists"""

def log_kpis_advanced(file_name,digraph,cumul_nodes,cumul_density,node_type_lists):
    """ Compute and log advanced Key Performance Indicators (KPIs) for a knowledge graph.
    
    This function calculates comprehensive graph metrics and logs detailed information
    about graph structure, node categorization, connectivity, and relationships. It
    provides advanced analytics including node type breakdowns and cumulative statistics
    for monitoring graph growth and complexity.
    
    Args:
        file_name (str): Name of the knowledge graph file being analyzed
        digraph (networkx.DiGraph): The directed graph to analyze
        cumul_nodes (int): Current cumulative count of nodes across multiple graphs
        cumul_density (float): Current cumulative density across multiple graphs  
        node_type_lists (list): List containing 6 sublists of categorized nodes:
                               [trouble_ticket_nodes, change_request_nodes, 
                                application_nodes, network_resource_nodes,
                                network_interface_nodes, network_link_nodes]
    
    Returns:
        tuple: (updated_cumul_nodes, updated_cumul_density)
            - updated_cumul_nodes (int): New cumulative node count
            - updated_cumul_density (float): New cumulative density
    
    Logged Metrics:
        Basic Graph Statistics:
        - Knowledge graph filename
        - Total number of nodes and edges
        - Cumulative node count across graphs
        - Degree histogram distribution
        - Number of self-loops
        
        Advanced KPIs:
        - Graph density (current and cumulative)
        - Average degree connectivity
        
        Detailed Structure:
        - All edges with subject, predicate, object data
        - Complete node list
        
        Node Type Categorization:
        - Trouble ticket nodes count and list
        - Change request nodes count and list  
        - Application nodes count and list
        - Network resource nodes count and list
        - Network interface nodes count and list
        - Network link nodes count and list
    
    Logging:
        Uses 'graph_kpi' logger to output structured information with clear
        section separators for easy parsing and analysis.
    
    Example:
        >>> node_lists = [tt_nodes, cr_nodes, app_nodes, nr_nodes, ni_nodes, nl_nodes]
        >>> cumul_n, cumul_d = log_kpis_advanced("graph.ttl", my_graph, 100, 0.5, node_lists)
        >>> # Logs comprehensive KPIs and returns updated cumulative values

    trouble_ticket_nodes, change_request_nodes, application_nodes,\
          network_resource_nodes, network_interface_nodes, network_link_nodes = node_type_lists

    logger = logging.getLogger('graph_kpi')

    logger.info('##################################################')
    logger.info('Knowledge Graph : %s',file_name)
    logger.info('Number of Nodes : %s',digraph.number_of_nodes())
    logger.info('Number of edges : %s',digraph.number_of_edges())
    cumul_nodes = cumul_nodes + digraph.number_of_nodes()
    logger.info('cumulative number of nodes : %s',cumul_nodes )
    logger.info('degree_histogram : %s', degree_histogram(digraph))
    logger.info('number of self loop : %s', number_of_selfloops(digraph))
    logger.info('####  KPIs ####')
    logger.info('DiGraph density : %s',density(digraph))
    cumul_density = cumul_density + density(digraph)
    logger.info('cumulative density : %s',cumul_density)
    logger.info('Average degree connectivity : %s', average_degree_connectivity(digraph))
    logger.info('#### Subject, Object, predicate ####')
    for s, p, data in digraph.edges(data=True):
        logger.info('%s,%s,%s',s,p,data)
    logger.info('#### NODES #### :%s',len(digraph.nodes))
    logger.info('%s',digraph.nodes)
    logger.info('trouble tickets nodes :%s',trouble_ticket_nodes)
    logger.info('change request nodes :%s',change_request_nodes)
    logger.info('application nodes :%s',application_nodes)
    logger.info('network resource nodes :%s',network_resource_nodes)
    logger.info('network interface nodes :%s',network_interface_nodes)
    logger.info('network link nodes :%s',network_link_nodes)
    logger.info('##################################################\n')

    return cumul_nodes, cumul_density"""

def log_kpis_basic(file_name,digraph,cumul_nodes,cumul_density):
    """ Compute and log basic Key Performance Indicators (KPIs) for a knowledge graph.
    
    This function calculates fundamental graph metrics and logs essential information
    about graph structure and connectivity. It provides core analytics without node
    type categorization, making it suitable for simple graph analysis and monitoring.
    
    Args:
        file_name (str): Name of the knowledge graph file being analyzed
        digraph (networkx.DiGraph): The directed graph to analyze
        cumul_nodes (int): Current cumulative count of nodes across multiple graphs
        cumul_density (float): Current cumulative density across multiple graphs
    
    Returns:
        tuple: (updated_cumul_nodes, updated_cumul_density)
            - updated_cumul_nodes (int): New cumulative node count
            - updated_cumul_density (float): New cumulative density
    
    Logged Metrics:
        Basic Graph Statistics:
        - Knowledge graph filename
        - Total number of nodes and edges  
        - Cumulative node count across graphs
        - Degree histogram distribution
        - Number of self-loops
        
        Core KPIs:
        - Graph density (current and cumulative)
        - Average degree connectivity
        
        Detailed Structure:
        - All edges with subject, predicate, object data
        - Complete node list with count
    
    Logging:
        Uses 'graph_kpi' logger to output structured information with clear
        section separators. Output is less detailed than log_kpis_advanced
        but covers essential graph metrics.
    
    Use Cases:
        - Quick graph analysis
        - Performance monitoring without categorization overhead
        - Basic graph comparison and tracking
        - When node type information is not needed
    
    Example:
        >>> cumul_n, cumul_d = log_kpis_basic("simple_graph.ttl", my_graph, 50, 0.3)
        >>> # Logs basic KPIs and returns updated cumulative values 

    logger = logging.getLogger('graph_kpi')

    logger.info('##################################################')
    logger.info('Knowledge Graph : %s',file_name)
    logger.info('Number of Nodes : %s',digraph.number_of_nodes())
    logger.info('Number of edges : %s',digraph.number_of_edges())
    cumul_nodes = cumul_nodes + digraph.number_of_nodes()
    logger.info('cumulative number of nodes : %s',cumul_nodes )
    logger.info('degree_histogram : %s', degree_histogram(digraph))
    logger.info('number of self loop : %s', number_of_selfloops(digraph))
    logger.info('####  KPIs ####')
    logger.info('DiGraph density : %s',density(digraph))
    cumul_density = cumul_density + density(digraph)
    logger.info('cumulative density : %s',cumul_density)
    logger.info('Average degree connectivity : %s', average_degree_connectivity(digraph))
    logger.info('#### Subject, Object, predicate ####')
    for s, p, data in digraph.edges(data=True):
        logger.info('%s,%s,%s',s,p,data)
    logger.info('#### NODES #### :%s',len(digraph.nodes))
    logger.info('%s',digraph.nodes)
    logger.info('##################################################\n')

    return cumul_nodes, cumul_density"""
