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
from rdflib import URIRef,Namespace

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

        print(count)
        print(nbr_file)

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
        blank_nodes = []

        for subj, pred, obj in g:
            #last_part_pred=get_last_folder_part(pred,'/')
            #print(last_part_pred)

            #if last_part_pred in datatypeproperties:
                #print(f'{last_part_pred} in DTP' )

            #if (('label' in last_part_pred) or ('type' in last_part_pred) or
            #    ('inScheme' in last_part_pred) or ('description' in last_part_pred) or
            #    ('comment' in last_part_pred) or last_part_pred in datatypeproperties):
            #    pass
            #else :
            #    last_part_subj=get_last_folder_part(subj,'/')
            #    last_part_obj=get_last_folder_part(obj,'/')
            #    nx_graph.add_edge(str(last_part_subj),str(last_part_obj),label=str(last_part_pred))

            if (isinstance(subj, URIRef) and isinstance(obj, URIRef) and (pred != rdf.type)\
                and (pred != rdfs.isDefinedBy) and pred not in datatypeproperties):
                #print(subj, pred, obj)
                nx_graph.add_edge(str(subj), str(obj), label=str(pred))
                #print(f"subj {subj}")
                #print(f"obj {obj}")

            #if isinstance(subj, BNode) and (pred != rdf.type) and subj not in blank_nodes:
                #and (pred != rdfs.isDefinedBy) and pred not in datatypeproperties:
                #print(rdf.type)
                #logger_node.info('Subject is a BN : %s, pred %s, object %s, file : %s',\
                    #subj,pred,obj,file)
                #logger_node.info('Blank node (pred) : %s',pred)
                #blank_nodes.append(subj)
                #blank_nodes.append(file)

            #if isinstance(obj, BNode) and (pred != rdf.type) and obj not in blank_nodes:
                #and (pred != rdfs.isDefinedBy) and pred not in datatypeproperties:
                #print(rdf.type)
                #logger_node.info('Object is a BN : %s, pred %s, subject %s, file : %s'\
                    #,obj,pred,subj,file)
                #blank_nodes.append(obj)
                #blank_nodes.append(file)
                #logger_node.info('Blank node (pred) : %s',pred)
                #logger_node.info('Blank node (object) : %s',obj)
                #for p, o in g.predicate_objects(subj):
                #    print(f"  - {p} {o}")
                #print(f"triples with blank node: {subj} {pred} {obj}")

        nodes=list(nx_graph.nodes)
        #print(file)
        #print(nodes)
        #print("\nGraph in Turtle format:")
        #print(g.serialize(format="turtle").encode("utf-8").decode("utf-8"))

        ### for gemini 2.5 flash ###
        nodes_no_url=[Path(nodes).name for nodes in nodes]
        all_nodes.append(nodes_no_url)
        #all_nodes.append(blank_nodes)
        #print(file)

        ### for gpt-4.1-nano ###
        #nodes_with_bracket = [f"<{nodes}>" for nodes in nodes]
        #all_nodes.append(nodes_with_bracket)

    # Transform list of list into a simple list
    all_nodes_list = [item for sublist in all_nodes for item in sublist]
    logger_node.info('\n all nodes list %s :',all_nodes_list)
    #logger_node.info('\n blank nodes list %s :',blank_nodes)
    #logger_node.info('\n blank nodes[0] %s type %s :',blank_nodes[0],type(blank_nodes[0]))

    #BNF = [node for node in blank_nodes if isinstance(node,BNode)]

    #logger_node.info('\n blank nodes filtered] %s  :',BNF)

    #all_nodes_list_unique = list(set(all_nodes_list))
    #print(f'NODES OF FINAL GRAPH : {all_nodes_list_unique} \n')

    counts=Counter(all_nodes_list)
    #print('COUNTS',counts['CustomerPortal'])
    dupplicate_nodes=[item for item, count in counts.items() if count > 1]
    #print('dupplicates_nodes_from_find',dupplicate_nodes)

    #print('duplicate_nodes',dupplicate_nodes)
    #print(f'NODE WITH DUPLICATE IN THE GENERATED GRAPH: {dupplicate_nodes} \n ' )

    return dupplicate_nodes

def occurence_duplicate(duplicates_nodes,path_result):
    '''compute the occurence of duplicates all over the ttl files once a node appear in a ttl file
    occu_duplicates is increased by 1'''
    occu_duplicates=[[duplicates_nodes[i],0] for i in range(0,len(duplicates_nodes))]
    #print('duplicates_nodes',duplicates_nodes)
    #print('occu_duplicate',occu_duplicates)

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
            #if item[0] in content:
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

    #occ_dup=occurence_duplicate(duplicates_nodes,path_result)

    while remain_occ != nbr_occ_max + 1:

        #occ_dup=occurence_duplicate(duplicates_nodes,path_result)
        #print('occ_dup',occ_dup)
        print('Treatment in progress for remain_occ =%s',remain_occ)

        #nbr_file_to_treat=nbr_occ_max-remain_occ
        occ_dup=occurence_duplicate(duplicates_nodes,path_result)
        nbr_file_treated=0
        os.makedirs(Path(f'{path_llm_graphs_dup_treated}/{remain_occ}'),exist_ok=True)

        #ttl_file_folder=Path(f'{path_result}/ttl_file_without_dup/{remain_occ}')
        #os.makedirs(ttl_file_folder,exist_ok=True)

        for ttl_file in all_ttl_files :
            dup_treated_list=[]

            logger_merge.info('##################################################')

            logger_merge.info('### REMAIN OCC ### = %s , nbr_occ_max = %s',remain_occ, nbr_occ_max)
            logger_merge.info('#### FILE ####: %s ', ttl_file)

            with open(Path(path_result)/ttl_file,'r',encoding='utf-8') as infile, \
                 open(f'{Path(path_llm_graphs_dup_treated)}/{remain_occ}/Treated_{remain_occ}_'\
                      f'{ttl_file}','w',encoding='utf-8') as outfile:

                logger_merge.info("nbr file treated %s",nbr_file_treated)
                #logger_merge.info('nbr_file_to_treat %s',nbr_file_to_treat)
                for line in infile:
                    dup1_treated=False
                    dup2_treated=False
                    logger_merge.info('Line : %s',line.strip())

                    for dup1 in occ_dup:

                        #if (dup1[0] in line) and (dup1[1]>remain_occ) and (dup1_treated is False):
                        if  re.search(r'\b' + re.escape(dup1[0]) + r'\b', line) and \
                            (dup1[1]>remain_occ) and (dup1_treated is False):

                            #if dup1[0]=="CustomerPortal":
                            #    print('customerportal',dup1[0])
                            #    print('line ',line)
                            #    if re.search(r'\b' + re.escape(dup1[0]) + r'\b', line):
                            #        print(f"'{dup1[0]}' is present as a whole word.")
                            #    else:
                            #        print(f"'{dup1[0]}' is NOT present as a whole word.")

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
                            #logger_merge.info('dup_treated_list %s',dup_treated_list[-1][0])

                        for dup2 in occ_dup: #case when there are 2 dup to rename in the same line
                            if (dup1_treated is True) and (dup2_treated is False) and\
                                  (dup2!=dup_treated_list[-1]) and\
                                      (dup2[0] not in dup_treated_list[-1][0]) and\
                                        (re.search(r'\b' + re.escape(dup2[0]) + r'\b',\
                                                    updated_line)) and (dup2[1]>remain_occ) :
                                        #(dup2[0] in updated_line) and (dup2[1]>remain_occ) :

                                #logger_merge.info('dup2 %s',dup2)
                                #logger_merge.info('dup_treated_list %s',dup_treated_list[-1])

                                updated_line_dual = updated_line.replace\
                                (dup2[0],f'{dup2[0]}_extra_node_{nbr_file_treated}')
                                # for gpt-4.1-nano
                                #(dup2[0],f'{dup2[0][:-1]}_extra_node_{nbr_file_treated}>')
                                #logger_merge.info('dup2 %s',dup2)
                                #logger_merge.info('dup1 %s',dup1)
                                logger_merge.info('updated_line_dual %s',updated_line_dual.strip())
                                outfile.write(updated_line_dual)
                                dup2_treated=True
                                dup_treated_list.append(dup2)

                    if dup1_treated is False or line=='\n':
                        outfile.write(line)
                        #logger_merge.info('Line : %s',line.strip())

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
                    #logger_merge.info('row_number %s',row_number)
                    #logger_merge.info('occ_dup[row_number][1] %s',occ_dup[row_number][1])
                    #logger_merge.info('occ_dup[row_number] %s',occ_dup[row_number])

                    occ_dup[row_number][1]=occ_dup[row_number][1]-1
                    logger_merge.info('occ_dup after %s',occ_dup)

                #logger_merge.info('occ_dup %s',occ_dup)

                #if dup1_treated is True:
                #    logger_merge.info(occ_dup[dup1[0]])
                #    occ_dup[dup1[0]][dup1[1]]=occ_dup[dup1[0]][dup1[1]-1]
                #    logger_merge.info(occ_dup[dup1[0]])

            #if dup1_treated is True:
            #    nbr_file_treated=nbr_file_treated+1
            nbr_file_treated=nbr_file_treated+1

        all_new_ttl_files = [f for f in Path(f'{path_llm_graphs_dup_treated}/{remain_occ}')\
            .iterdir() if f.is_file()]
        #print(all_new_ttl_files)
        #print(Path(path_llm_graphs_dup_treated))

        # merge mofified ttl file in an only one file
        merged_file=f'{path_merged}/merged_graph_{remain_occ}.ttl'
        #print(merged_file)
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
