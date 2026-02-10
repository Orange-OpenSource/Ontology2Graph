# Software Name : Ontologie2Graph
# SPDX-FileCopyrightText: Copyright (c) Orange SA
# SPDX-License-Identifier: BSD-4-Clause
#
# This software is distributed under the BSD 4-Clause "Original" or "Old" License,
# see the "LICENSE" file for more details or <license-url

''' Utils module for merging TTL (Turtle) files containing RDF graphs.

This module provides utility functions for:
- Building file and folder paths for merged graphs
- Managing prefixes in merged graphs  
- Finding homonymous nodes across multiple graphs
- Renaming homonyms to generate graphs with different densities
- Merging TTL files while handling duplicates

Functions:
    build_merged_folder_paths_and_files: Create necessary folders and file paths
    manage_prefix: Remove homonymous prefixes from merged files
    find_homonymes_nodes: Identify duplicate nodes across TTL files
    rename_and_merge: Rename homonymous nodes and merge files
    rename_homonyme_by_line: Internal function to replace homonyms line by line
    merge_graph: Merge multiple TTL files into a single file

Dependencies:
    - pathlib.Path: For cross-platform file path handling
    - collections.Counter: For counting node occurrences
    - rdflib: For RDF/Turtle format processing (URIRef, Namespace, BNode)
    - utils_common: Common utilities module '''

import datetime
import re
import os
import shutil
from pathlib import Path
from collections import Counter
import networkx as nx
import rdflib
from rdflib import URIRef,Namespace,BNode
from utils_common import utils as utils_common

def build_merged_folder_paths_and_files(path_files):
    ''' Create merged folder structure and return paths for processing TTL files.
    
    Creates necessary directories for:
    - Merged TTL files
    - Files with bad Turtle syntax
    - Processed files with homonym treatment
    - Log files
    
    Args:
        path_files (str): Base path where TTL files are stored
        
    Returns:
        tuple: Contains paths for:
            - bad_path_result (Path): Directory for invalid TTL files
            - log_file (Path): Main log file path
            - log_file_homonymes (Path): Homonym processing log file
            - log_file_check_ttl (Path): TTL validation log file  
            - path_merged (Path): Directory for merged files
            - path_homonyme_treated (str): Directory for homonym-treated files
            - create merged folder if not exists'''

    path_merged = f'{path_files}/merged'
    bad_path_result = f'{path_files}/Invalid_Turtle_Syntax_for_merged_graphs'
    path_homonyme_treated=f'{Path(path_merged)}/homonymes_treated'
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file=f'{Path(path_files)}/logs/merge_graph_{date}.log'
    log_file_homonymes=f'{Path(path_files)}/logs/homonymes_graph_{date}.log'
    log_file_check_ttl=f'{Path(path_files)}/logs/check_merged_ttl_graph_{date}.log'

    if os.path.exists(path_merged):
        shutil.rmtree(path_merged)
    os.makedirs(Path(path_merged))

    if os.path.exists(bad_path_result):
        shutil.rmtree(bad_path_result)
    os.makedirs(Path(bad_path_result))

    ### remove previous log files homonyme in logs ###
    for filename in os.listdir(Path(log_file).parent):
        if filename.startswith('merge_graph_') or filename.startswith('homonymes')\
            or filename.startswith('check'):
            file_path = os.path.join(Path(log_file).parent, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

    return(bad_path_result,Path(log_file),Path(log_file_homonymes),Path(log_file_check_ttl),\
        Path(path_merged),path_homonyme_treated)

def manage_prefix(path_merged):
    ''' Remove homonymous prefixes from merged TTL files.
    
    Processes all TTL files in the merged directory to:
    - Extract and deduplicate prefix declarations
    - Separate node definitions from prefixes
    - Rewrite files with unique prefixes
    
    Args:
        path_merged (str): Path to directory containing merged TTL files
        
    Note:
        Modifies merged files in place by rewriting them with deduplicated prefixes'''

    nodes_lines=[]
    prefix_lines=[]
    prefix_lines_unique=[]

    nbr_file = 0

    with os.scandir(path_merged) as entries:
        for entry in entries:
            if entry.is_file():
                nbr_file += 1

    count = 0
    while count != nbr_file :

        merged_file_list = [f.name for f in Path(f'{path_merged}').iterdir() if f.is_file()]
        merged_file=f'{path_merged}/{merged_file_list[count]}'

        with open (merged_file, 'r', encoding='utf-8') as outfile:
            lines = outfile.readlines()
            prefix_lines = [lines for lines in lines if lines.startswith('@')]
            nodes_lines= [lines for lines in lines if not lines.startswith('@')]
            outfile.close()

    ### remove homonyme prefix ###
        for item in prefix_lines:
            if item not in prefix_lines_unique:
                prefix_lines_unique.append(item)

        with open (merged_file, 'w', encoding='utf-8') as graph:
            graph.writelines(prefix_lines_unique)
            graph.writelines(nodes_lines)
            graph.close()
        count = count + 1

def find_homonymes_nodes(path,logger_homonymes,ontology):
    ''' Find homonymous nodes across multiple TTL files.
    
    Analyzes all TTL files in the specified path to identify nodes that appear in multiple
     graphs. Counts the number of files in which each homonymous node appears.
    
    Args:
        path (str): Directory path containing TTL files to analyze
        logger_homonymes: Logger instance for recording homonym information
        ontology: Ontology object for retrieving datatype properties
        
    Returns:
        Counter: Dictionary-like object mapping node names to their occurrence counts
        
    Example:
        >>> homonymes = find_homonymes_nodes('/path/to/ttl/files', logger, onto)
        >>> homonymes['NodeA']  # Returns number of files containing NodeA '''

    ### List all the ttl graph files in PATH except folder ###
    all_files = [f.name for f in Path(path).iterdir() if f.is_file()]

    ### Retreive DatatypeProperties from ontology ###
    dtp=utils_common.retreive_onto_object(ontology,"DatatypeProperty")

    ### Rebuild complete file path (folder/file) ###
    for i, file in enumerate(all_files):
        all_files[i]= f'{path}/{file}'

    all_nodes_of_all_graphs=[]

    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    skos = Namespace("http://www.w3.org/2004/02/skos/core#")

    for file in all_files :

        g = rdflib.Graph()
        g.parse(file, format="turtle")

        nx_graph = nx.DiGraph()
        nodes_name=[]
        ### populate the networkx graph ###
        for subj, pred, obj in g:
            if (isinstance(subj, URIRef) and isinstance(obj, URIRef) and (pred != rdf.type) and\
                (pred != skos.inScheme) and (pred != rdfs.isDefinedBy) and pred not in dtp):
                nx_graph.add_edge(str(subj), str(obj), label=str(pred))

            ### taken ito account blank nodes ###
            if isinstance(subj, BNode) and (pred != rdf.type) and (pred != skos.inScheme):
                for subjbn, predbn in g.subject_predicates(subj):
                    short_subjbn=Path(str(subjbn)).name
                    short_predbn=Path(str(predbn)).name
                    logger_homonymes.info('Blank Node Subject:%s,Predicate :%s,Object : %s',\
                        short_subjbn,short_predbn,obj)
                    nx_graph.add_edge(str(subjbn),str(obj),label=str(predbn),color='white')

        nodes_name=[os.path.basename(Path(n)) for n in list(nx_graph.nodes)]
        nodes_name_final=[s.split('#',1)[1] if '#' in s else s for s in nodes_name]

        ### remove duplicate to keep only the name of the nodes that appears at least ###
        ### once in a file ###
        nodes_name_per_file=set(nodes_name_final)

        logger_homonymes.info('nodes in : %s \n',file)
        logger_homonymes.info('%s \n',nodes_name_final)

        all_nodes_of_all_graphs.append(nodes_name_per_file)

    ### Transform list of list into a simple list ###
    all_nodes_of_all_graphs_list=[item for sublist in all_nodes_of_all_graphs for item in sublist]

    logger_homonymes.info('All the nodes of all the graph : ')
    logger_homonymes.info(all_nodes_of_all_graphs_list)

    homonyme_occurence=Counter(all_nodes_of_all_graphs_list)
    logger_homonymes.info('\n homonymes nodes list and occurence %s :',homonyme_occurence)

    return homonyme_occurence

def rename_and_merge(path_homonyme_treated,path_merged,homonymes_nodes_and_occurence,\
    nbr_homonyme_max,logger_merge):
    ''' Rename homonymous nodes and merge TTL files with varying density levels.
    
    Creates multiple versions of merged graphs by progressively reducing the number
    of homonymous nodes.
    
    Args:
        path_homonyme_treated (str): Output directory for processed files
        path_merged (Path): Directory containing original merged files
        homonymes_nodes_and_occurence (Counter): Node occurrence counts
        nbr_homonyme_max (int): Maximum number of homonymous occurrences
        logger_merge: Logger instance for merge operations
        
    Returns:
        list: Names of newly created TTL files with homonym treatment
        
    Note:
        Creates multiple merged files with suffix indicating homonym threshold '''

    path_files=path_merged.parent

    all_ttl_files = [f.name for f in Path(path_files).iterdir() if f.is_file()]
    all_new_ttl_files = []
    max_occ_for_file_to_merge=1 #useless to start at 0

    os.system("clear")
    print('Merging Treatment in progress :')
    print('At least one homonyme node appeared in : ', nbr_homonyme_max,' differents files \n')

    while max_occ_for_file_to_merge != nbr_homonyme_max + 1:

        if max_occ_for_file_to_merge == 1:
            print('Renaming all the homonymes and merging')
        else :
            print(f'Keeping {max_occ_for_file_to_merge} homonyme max in {max_occ_for_file_to_merge}\
                different files and merging' )

        os.makedirs(Path(f'{path_homonyme_treated}/{max_occ_for_file_to_merge}'),exist_ok=True)

        occ_dup=homonymes_nodes_and_occurence.copy()
        nbr_file_treated=0

        for ttl_file in all_ttl_files :
            dup_treated_list=[]

            logger_merge.info('##################################################################')
            logger_merge.info('Target number of max homonyme in the set of files = %s',\
                max_occ_for_file_to_merge)
            logger_merge.info('Max number of homonyme in the set of files : %s',nbr_homonyme_max)
            logger_merge.info('#### FILE ####: %s',  ttl_file)

            with open(Path(path_files)/ttl_file,'r',encoding='utf-8') as infile,\
                 open(f'{Path(path_homonyme_treated)}/{max_occ_for_file_to_merge}/Treated_'\
                      f'{max_occ_for_file_to_merge}_{ttl_file}','w',encoding='utf-8') as outfile:
                rename_homonyme_by_line(infile,outfile,max_occ_for_file_to_merge,occ_dup,\
                        dup_treated_list,logger_merge,nbr_file_treated)

            ### remove homonyme in dup_treated_list ###
            unique_set=set(dup_treated_list)
            unique_dup_treated_list=list(unique_set)

            ### decrease occurence in occ_dup ###
            for dup_treated in unique_dup_treated_list:
                if dup_treated in occ_dup:
                    occ_dup[dup_treated]=occ_dup[dup_treated]-1

            print(f'{ttl_file} treated')
            logger_merge.info('occ_dup after treatement %s',occ_dup)
            nbr_file_treated=nbr_file_treated+1

        all_new_ttl_files=[f for f in Path(f'{path_homonyme_treated}/{max_occ_for_file_to_merge}')\
            .iterdir() if f.is_file()]

        ### merge files in an only one ###
        merge_graph(all_new_ttl_files,path_merged,max_occ_for_file_to_merge)

        max_occ_for_file_to_merge = max_occ_for_file_to_merge + 1
    return all_new_ttl_files

### Functions used internally in utils.py ###

def rename_homonyme_by_line(infile,outfile,homo_max,occ_dup,dup_treated_list,logger_merge,
                            nbr_file_treated):
    ''' Replace homonymous nodes line by line in TTL files.
    
    Internal function that processes TTL content line by line, identifying and
    replacing homonymous nodes according to the specified threshold.
    
    Args:
        infile: Input file handle for reading original TTL content
        outfile: Output file handle for writing processed TTL content
        homo_max (int): Maximum allowed homonym occurrences
        occ_dup: Occurrence data for duplicate nodes
        dup_treated_list: List of already processed duplicates
        logger_merge: Logger for recording merge operations
        nbr_file_treated (int): Count of files processed so far
        
    Note:
        This is an internal utility function called by rename_and_merge '''

    for line in infile:

        dup_treated=False
        logger_merge.info('Line : %s',line.strip())

        if line =='\n' or line.startswith('#') or line.startswith('@') or \
            line.startswith('    rdfs:comment') or line.startswith('    rdfs:label') or \
                line.startswith('    rdfs:seeAlso') or line.startswith('    skos:example'):
            outfile.write(line)
        else :

            if '#' in line: #remove comment start with '#' at the end of the line
                line=line.split(' #',1)[0]

            updated_line=line
            for key, value in occ_dup.items():

                if re.search(r'\b' + re.escape(key) + r'\b', line)\
                  and (value>homo_max):
                    updated_line = updated_line.replace\
                        (key,f'{key}_extra_node_{nbr_file_treated}')
                    logger_merge.info('dup %s %s',key,value)
                    logger_merge.info('updated_line %s',updated_line.strip())
                    dup_treated_list.append(key)
                    dup_treated=True

            if dup_treated is True :
                outfile.write(updated_line)
            else :
                outfile.write(line)

def merge_graph(all_new_ttl_files,path_merged,homo_max):
    ''' Merge multiple TTL files into a single combined graph file.
    
    Combines all processed TTL files into one merged file, maintaining
    proper Turtle syntax and formatting.
    
    Args:
        all_new_ttl_files (list): List of TTL file names to merge
        path_merged (Path): Output directory for merged file
        homo_max (int): Homonym threshold used (for filename suffix)
        
    Returns:
        str: Path to the created merged file
        
    Note:
        Creates a file named 'merged_graph_{homo_max}.ttl' '''

    merged_file=f'{path_merged}/merged_graph_{homo_max}.ttl'
    with open(merged_file, 'w', encoding='utf-8') as m_file:
        for file in all_new_ttl_files: # Open each input file in read mode

            with open(file, 'r', encoding='utf-8')\
             as ttl_file: # Read the content and write it to the output file
                content = ttl_file.read()
                m_file.write(content)
                m_file.write('\n')  # Adds a newline between files
    print('Graphs have been merged successfully.\n')
