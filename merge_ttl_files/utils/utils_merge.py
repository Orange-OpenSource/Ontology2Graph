'''list of function to be used '''

import logging
import re
import os
import shutil
from pathlib import Path
import subprocess
from collections import Counter
import networkx as nx
import rdflib
from rdflib import URIRef,Namespace,BNode

def remove_pred_obj(expr, graph, predi, obje):
    '''remove predicate and target object of an edge'''
    edges_to_remove = [(u, v) for u, v, attr in graph.edges(data=True)
                         if attr.get(expr) == predi and v == obje]
    return graph.remove_edges_from(edges_to_remove)

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

def check_ttl(path_merged,bad_path_result,merged):
    '''check ttl syntax and store wrong file in specific folder'''

    nbr_file = 0

    with os.scandir(path_merged) as entries:
        for entry in entries:
            if entry.is_file():
                nbr_file += 1

    count = 0

    merged_file_list = [f.name for f in Path(path_merged).iterdir() if f.is_file()]
    print(merged_file_list)

    while count != nbr_file:

        merged_file=f'{path_merged}/{merged_file_list[count]}'

        command=["ttl",merged_file]
        ttlvalidator=subprocess.Popen(command, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,text=True)
        stdout, stderr = ttlvalidator.communicate()
        if merged==1:
            print(f'Merged graph {Path(merged_file).name} : Turtle validator Result: \
                  {stdout},{stderr}\n')
        else:
            print(f'Turtle validator Result: {stdout}, {stderr}')

        if stdout!='Validator finished with 0 warnings and 0 errors.\n' :
        # move bad file in bad folder and Save logs
            bad_merged_file=f'{bad_path_result}/merged_graph_{count}_BAD.ttl'
            print('bad_merged_file : ', bad_merged_file)

            os.makedirs(f'{bad_path_result}', exist_ok=True)
            shutil.move(merged_file, bad_merged_file)

            with open(f'{bad_path_result}/errors.log', 'a',encoding='utf-8') as log:
                log.write(f'{bad_merged_file} : {ttlvalidator.communicate()}\n')
                log.close()
        count = count + 1

def get_last_folder_part(string, sep_char):
    """get last part of a folder string"""
    string_parts=string.split(sep_char)
    last_part=string_parts[len(string_parts)-1]
    if last_part=='':
        last_part=string_parts[len(string_parts)-2]
    return last_part

def manage_prefix(path_merged):
    '''remove duplicate prefix of the merged file'''
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

        #path_merged_count=f'{path_merged}/'
        merged_file_list = [f.name for f in Path(f'{path_merged}').iterdir() if f.is_file()]
        merged_file=f'{path_merged}/{merged_file_list[count]}'

        with open (merged_file, 'r', encoding='utf-8') as outfile:
            lines = outfile.readlines()
            prefix_lines = [lines for lines in lines if lines.startswith('@')]
            nodes_lines= [lines for lines in lines if not lines.startswith('@')]
            outfile.close()

    #remove duplicate prefix
        for item in prefix_lines:
            if item not in prefix_lines_unique:
                prefix_lines_unique.append(item)

        with open (merged_file, 'w', encoding='utf-8') as graph:
            graph.writelines(prefix_lines_unique)
            graph.writelines(nodes_lines)
            graph.close()
        count = count + 1

def find_duplicates_nodes(path,ontology):
    '''find duplicates nodes in ttl files, just add the folder where the files
    are stored as an argument'''

    # List all the ttl graph files in PATH except folder
    all_files = [f.name for f in Path(path).iterdir() if f.is_file()]

    datatypeproperties=retreive_datatype_properties(ontology)
    skos = Namespace("http://www.w3.org/2004/02/skos/core#")

    # Rebuild complete file path (folder/file)
    for i, file in enumerate(all_files):
        all_files[i]= f'{path}/{file}'

    all_nodes=[]
    nodes=[]
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

    path_node_log=Path(f'{path}/nodes_log')
    if os.path.exists(path_node_log):
        shutil.rmtree(path_node_log)
    os.makedirs(path_node_log)

    #set logger
    log_file=Path(f'{path_node_log}/node.log')
    if log_file.is_file():
        os.remove(log_file)

    logger_node = logging.getLogger('Node_log')
    handler = logging.FileHandler(log_file)
    logger_node.setLevel(logging.INFO)
    logger_node.addHandler(handler)

    for file in all_files :

        g = rdflib.Graph()
        g.parse(file, format="turtle")

        nx_graph = nx.DiGraph()

        for subj, pred, obj in g:

            if (isinstance(subj, URIRef) and isinstance(obj, URIRef) and (pred != rdf.type) #and (pred != skos.inScheme)
                and (pred != rdfs.isDefinedBy) and pred not in datatypeproperties):
                nx_graph.add_edge(str(subj), str(obj), label=str(pred))

        #if isinstance(subj, BNode) and (pred != rdf.type) and (pred != skos.inScheme):
        #    for subjbn, predbn in g.subject_predicates(subj):
                #short_subjbn=Path(subjbn).name
                #short_predbn=Path(predbn).name
                #logger_file1.info('Blank Node Subject:%s,Predicate :%s,Object : %s',subj,pred,obj)
        #        nx_graph.add_edge(str(subjbn),str(obj),label=str(predbn),\
        #            color='white')

        nodes=list(nx_graph.nodes)

        ### for gemini 2.5 flash ###
        nodes_no_url=[Path(nodes).name for nodes in nodes]
        all_nodes.append(nodes_no_url)

        ### for gpt-4.1-nano ###
        #nodes_with_bracket = [f"<{nodes}>" for nodes in nodes]
        #all_nodes.append(nodes_with_bracket)

    # Transform list of list into a simple list
    all_nodes_list = [item for sublist in all_nodes for item in sublist]
    logger_node.info('\n all nodes list %s :',all_nodes_list)

    counts=Counter(all_nodes_list)
    dupplicate_nodes=[item for item, count in counts.items() if count > 1]

    return dupplicate_nodes

def occurence_duplicate(duplicates_nodes,path_result):
    '''compute the occurence of duplicates all over the ttl files once a node appear in a ttl file
    occu_duplicates is increased by 1'''
    occu_duplicates=[[duplicates_nodes[i],0] for i in range(0,len(duplicates_nodes))]

    #List all the ttl graph files in PATH except folder
    all_files = [f.name for f in Path(path_result).iterdir() if f.is_file()]

    #rebuild complete file path (folder/file)
    for i, file in enumerate(all_files):
        all_files[i]= f'{path_result}/{file}'

    for file in all_files:

        with open(file,'r',encoding='utf-8') as file:
            content = file.read()

        for item in occu_duplicates:
            if re.search(r'\b' + re.escape(item[0]) + r'\b', content):
                item[1]=item[1]+1

        file.close()
    return occu_duplicates

def merge_ttl_graphs(path_result,path_merged,duplicates_nodes,nbr_occ_max):
    ''' rename the duplicated nodes by varying remain_occ parameter from 0 to nbr_occ_max. Then for
    each iteration merged all the new ttl files in an only one file'''

    all_ttl_files = [f.name for f in Path(path_result).iterdir() if f.is_file()]

    if os.path.exists(path_merged):
        shutil.rmtree(path_merged)
    os.makedirs(Path(path_merged))

    path_llm_graphs_dup_treated=f'{Path(path_result)}/llm_graphs_dup_treated'
    if os.path.exists(path_llm_graphs_dup_treated):
        shutil.rmtree(path_llm_graphs_dup_treated)
    os.makedirs(path_llm_graphs_dup_treated)

    path_merged_log=Path(f'{path_merged}/merge_log')
    if os.path.exists(path_merged_log):
        shutil.rmtree(path_merged_log)
    os.makedirs(path_merged_log)

    #set logger
    log_file=Path(f'{path_merged_log}/merge.log')
    if log_file.is_file():
        os.remove(log_file)

    logger_merge = logging.getLogger('Merge_log')
    handler = logging.FileHandler(log_file)
    logger_merge.setLevel(logging.INFO)
    logger_merge.addHandler(handler)

    remain_occ=1

    while remain_occ != nbr_occ_max + 1:

        print('Treatment in progress for remain_occ =%s',remain_occ)

        occ_dup=occurence_duplicate(duplicates_nodes,path_result)
        nbr_file_treated=0
        os.makedirs(Path(f'{path_llm_graphs_dup_treated}/{remain_occ}'),exist_ok=True)

        for ttl_file in all_ttl_files :
            dup_treated_list=[]

            logger_merge.info('##################################################')

            logger_merge.info('### REMAIN OCC ### = %s , nbr_occ_max = %s',remain_occ, nbr_occ_max)
            logger_merge.info('#### FILE ####: %s ', ttl_file)

            with open(Path(path_result)/ttl_file,'r',encoding='utf-8') as infile, \
                 open(f'{Path(path_llm_graphs_dup_treated)}/{remain_occ}/Treated_{remain_occ}_'\
                      f'{ttl_file}','w',encoding='utf-8') as outfile:

                logger_merge.info("nbr file treated %s",nbr_file_treated)
                for line in infile:
                    dup1_treated=False
                    dup2_treated=False
                    logger_merge.info('Line : %s',line.strip())

                    for dup1 in occ_dup:

                        if  re.search(r'\b' + re.escape(dup1[0]) + r'\b', line) and \
                            (dup1[1]>remain_occ) and (dup1_treated is False):

                            updated_line = line.replace\
                                (dup1[0],f'{dup1[0]}_extra_node_{nbr_file_treated}')
                                # for gpt-4.1-nano
                                #(dup1[0],f'{dup1[0][:-1]}_extra_node_{nbr_file_treated}>')
                            logger_merge.info('dup1 %s',dup1)
                            logger_merge.info('remain_occ %s',remain_occ)
                            logger_merge.info('updated_line %s',updated_line.strip())
                            logger_merge.info('file : %s',infile)
                            dup1_treated=True
                            dup_treated_list.append(dup1)

                        for dup2 in occ_dup: #case when there are 2 dup to rename in the same line
                            if (dup1_treated is True) and (dup2_treated is False) and\
                                  (dup2!=dup_treated_list[-1]) and\
                                      (dup2[0] not in dup_treated_list[-1][0]) and\
                                        (re.search(r'\b' + re.escape(dup2[0]) + r'\b',\
                                                    updated_line)) and (dup2[1]>remain_occ) :

                                updated_line_dual = updated_line.replace\
                                (dup2[0],f'{dup2[0]}_extra_node_{nbr_file_treated}')

                                logger_merge.info('updated_line_dual %s',updated_line_dual.strip())
                                outfile.write(updated_line_dual)
                                dup2_treated=True
                                dup_treated_list.append(dup2)

                    if dup1_treated is False or line=='\n':
                        outfile.write(line)

                    if dup1_treated is True and dup2_treated is False:
                        outfile.write(updated_line)

            # remove duplicate in dup_treated_list
            unique_tuple = {tuple(sublist) for sublist in dup_treated_list}
            unique_dup_treated_list=[list(t) for t in unique_tuple ]
            logger_merge.info('unique_dup_treated_list : %s',unique_dup_treated_list)

            # decrease occurence in occ_dup
            logger_merge.info('occ_dup %s',occ_dup)
            for dup_treated in unique_dup_treated_list:
                logger_merge.info('dup_treated %s',dup_treated)
                if dup_treated in occ_dup:
                    row_number=occ_dup.index(dup_treated)

                    occ_dup[row_number][1]=occ_dup[row_number][1]-1
                    logger_merge.info('occ_dup after %s',occ_dup)

            nbr_file_treated=nbr_file_treated+1

        all_new_ttl_files = [f for f in Path(f'{path_llm_graphs_dup_treated}/{remain_occ}')\
            .iterdir() if f.is_file()]

        # merge mofified ttl file in an only one file
        merged_file=f'{path_merged}/merged_graph_{remain_occ}.ttl'
        with open(merged_file, 'w', encoding='utf-8') as m_file:
            for file in all_new_ttl_files: # Open each input file in read mode
                with open(file, 'r', encoding='utf-8')\
                 as ttl_file: # Read the content and write it to the output file
                    content = ttl_file.read()
                    m_file.write(content)
                    m_file.write('\n')  # Adds a newline between files

        remain_occ = remain_occ + 1

def max_node_occ_value(ttl_folder,ontology):
    '''return the node that have the max occurrence'''

    duplicate_nodes=find_duplicates_nodes(ttl_folder,ontology)

    occ_dup=occurence_duplicate(duplicate_nodes,ttl_folder)

    if occ_dup != []:
        print(f'List of all the nodes that appeared in several ttl files : {occ_dup} ')
        m_n_o_v = max(sublist[1] for sublist in occ_dup)
        print('Max number of occurence of nodes in ttl files:', m_n_o_v)
        node_max_occ=[sublist[0] for sublist in occ_dup if sublist[1] == m_n_o_v]
        print('Node that have the max number of occurence in ttl files :',node_max_occ)

    else:
        print('NO DUPLICATES NODES FOUND')
        node_max_occ='NULL'
        m_n_o_v = 0

    return m_n_o_v, node_max_occ
