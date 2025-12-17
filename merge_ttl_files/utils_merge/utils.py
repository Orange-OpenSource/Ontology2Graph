'''list of function to be used '''

import datetime
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

def check_ttl(path_merged,bad_path_result,logger_check_ttl):
    '''check ttl syntax and store wrong file in specific folder'''

    nbr_file = 0

    with os.scandir(path_merged) as entries:
        for entry in entries:
            if entry.is_file():
                nbr_file += 1
    print('Number of merged file to check : %s',nbr_file)

    count = 0
    bad_file = 0

    merged_file_list = [f.name for f in Path(path_merged).iterdir() if f.is_file()]

    while count != nbr_file:

        merged_file=f'{path_merged}/{merged_file_list[count]}'

        command=["ttl",merged_file]
        ttlvalidator=subprocess.Popen(command, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,text=True)
        stdout, stderr = ttlvalidator.communicate()
        logger_check_ttl.info('Merged graph %s : Turtle validator Result: %s,%s\n',\
                              Path(merged_file).name,stdout,stderr)

        if stdout!='Validator finished with 0 warnings and 0 errors.\n' :
        # move bad file in bad folder and Save logs
            bad_merged_file=f'{bad_path_result}/merged_graph_{count}_BAD.ttl'
            logger_check_ttl.info('bad_merged_file : %s', bad_merged_file)

            os.makedirs(f'{bad_path_result}', exist_ok=True)
            shutil.move(merged_file, bad_merged_file)

            logger_check_ttl.info('Error detected in %s', Path(merged_file).name)
            logger_check_ttl.info('Result: %s', stdout) 
            bad_file = bad_file + 1

        count = count + 1

    if bad_file == 0:
        print('\n No bad merged file detected')
    else:
        print(f'\n Number of bad merged files detected : {bad_file}')

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

def find_homonymes_nodes(path,logger_homonymes,ontology):
    '''find duplicates nodes in ttl files, just add the folder where the files
    are stored as an argument'''

    # List all the ttl graph files in PATH except folder
    all_files = [f.name for f in Path(path).iterdir() if f.is_file()]

    # Retreive DatatypeProperties from ontology
    dtp=retreive_datatype_properties(ontology)

    # Rebuild complete file path (folder/file)
    for i, file in enumerate(all_files):
        all_files[i]= f'{path}/{file}'

    all_nodes=[]
    nodes=[]
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    skos = Namespace("http://www.w3.org/2004/02/skos/core#")

    skosnumber=0

    for file in all_files :

        g = rdflib.Graph()
        g.parse(file, format="turtle")

        nx_graph = nx.DiGraph()
        nx_graphbn = nx.DiGraph()

        for subj, pred, obj in g:

            #print("subj %s", subj)
            logger_homonymes.info('\n subj %s :',subj)
            if (isinstance(subj, URIRef) and isinstance(obj, URIRef) and (pred != rdf.type) and\
                (pred != skos.inScheme) and (pred != rdfs.isDefinedBy) and pred not in dtp):
                nx_graph.add_edge(str(subj), str(obj), label=str(pred))

            if not isinstance(subj, BNode) and pred == skos.inScheme:
                skosnumber=skosnumber+1

            if isinstance(subj, BNode) and (pred != rdf.type) and (pred != skos.inScheme):
                for subjbn, predbn in g.subject_predicates(subj):
                    short_subjbn=Path(str(subjbn)).name
                    short_predbn=Path(str(predbn)).name
                    logger_homonymes.info('Blank Node Subject:%s,Predicate :%s,Object : %s',\
                        short_subjbn,short_predbn,obj)
                    nx_graph.add_edge(str(subjbn),str(obj),label=str(predbn),color='white')

        nodes=list(nx_graph.nodes)
        print('skosnumber : %s',skosnumber)
        logger_homonymes.info('\n nodes %s :',nodes)

        nodes_name=[Path(nodes).name for nodes in nodes]

        #Remove # character from node names if any
        nodes_name_final=[s.split('#',1)[1] if '#' in s else s for s in nodes_name]

        all_nodes.append(nodes_name_final)

    # Transform list of list into a simple list
    all_nodes_list = [item for sublist in all_nodes for item in sublist]
    logger_homonymes.info('\n all nodes list %s :',all_nodes_list)

    counts=Counter(all_nodes_list)
    homonymes_nodes=[item for item, count in counts.items() if count > 1]
    logger_homonymes.info('\n homonymes nodes list %s :',homonymes_nodes)

    return homonymes_nodes

def occurence_duplicate(homonymes_nodes,path_result):
    '''compute the occurence of duplicates all over the ttl files once a node appear in a ttl file
    occu_duplicates is increased by 1'''
    occu_duplicates=[[homonymes_nodes[i],0] for i in range(0,len(homonymes_nodes))]

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
    print('occu%s  ',occu_duplicates)

    print('len occu %s',len(occu_duplicates))

    return occu_duplicates

def build_merged_folder_paths_and_files(path_files):
    ''' create merged folder if not exists'''

    path_merged = f'{path_files}/merged'
    bad_path_result = f'{path_files}/Bad_Turtle_Syntax'
    path_duplicate_treated=f'{Path(bad_path_result)}/llm_graphs_dup_treated'
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

    if os.path.exists(path_duplicate_treated):
        shutil.rmtree(path_duplicate_treated)
    os.makedirs(path_duplicate_treated)

    ### remove previous log files homonyme ###
    for filename in os.listdir(Path(log_file).parent):
        if filename.startswith('merge_graph_') or filename.startswith('homonymes')\
            or filename.startswith('check'):
            file_path = os.path.join(Path(log_file).parent, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

    return(bad_path_result,Path(log_file),Path(log_file_homonymes),Path(log_file_check_ttl),Path(path_merged),\
           path_duplicate_treated)

def rename_homonyme_by_line(infile,outfile,remain_occ,occ_dup,dup_treated_list,logger,\
                            nbr_file_treated):
    '''check if homonyme exists in line and replace it'''
    for line in infile:

        dup_treated=False
        logger.info('Line : %s',line.strip())

        if line =='\n' or line.startswith('#') or line.startswith('@'):
            outfile.write(line)
        else :
            updated_line=line
            for dup in occ_dup:
                if  re.search(r'\b' + re.escape(dup[0]) + r'\b', line) and (dup[1]>remain_occ):
                    updated_line = updated_line.replace\
                        (dup[0],f'{dup[0]}_extra_node_{nbr_file_treated}')
                    logger.info('dup %s',dup)
                    logger.info('remain_occ %s',remain_occ)
                    logger.info('updated_line %s',updated_line.strip())
                    logger.info('file : %s',infile)
                    dup_treated_list.append(dup)
                    dup_treated=True

            if dup_treated is True :
                outfile.write(updated_line)
            else :
                outfile.write(line)

def rename_homonyme_in_files(path_duplicate_treated,path_merged,duplicates_nodes,nbr_occ_max,logger_merge):
    ''' rename the duplicated nodes by varying remain_occ parameter from 0 to nbr_occ_max. Then for
    each iteration merged all the new ttl files in an only one file'''

    path_files=path_merged.parent

    all_ttl_files = [f.name for f in Path(path_files).iterdir() if f.is_file()]
    remain_occ=0

    while remain_occ != nbr_occ_max + 1:

        print('Treatment in progress for remain_occ =%s',remain_occ)
        os.makedirs(Path(f'{path_duplicate_treated}/{remain_occ}'),exist_ok=True)

        occ_dup=occurence_duplicate(duplicates_nodes,path_files)
        nbr_file_treated=0

        logger_merge.info('occ_dup_BN %s',occ_dup)

        for ttl_file in all_ttl_files :
            dup_treated_list=[]

            logger_merge.info('##################################################')
            logger_merge.info('### REMAIN OCC ### = %s , nbr_occ_max = %s',remain_occ, nbr_occ_max)
            logger_merge.info('#### FILE ####: %s ', ttl_file)

            print('REMAIN OCC : %s', remain_occ)
            print('File : %s', ttl_file)

            with open(Path(path_files)/ttl_file,'r',encoding='utf-8') as infile, \
                 open(f'{Path(path_duplicate_treated)}/{remain_occ}/Treated_{remain_occ}_'\
                      f'{ttl_file}','w',encoding='utf-8') as outfile:

                logger_merge.info("nbr file treated %s",nbr_file_treated)

                ##check if homonyme exists in line and replace it
                rename_homonyme_by_line(infile,outfile,remain_occ,occ_dup,dup_treated_list,\
                                        logger_merge,nbr_file_treated)

                #for line in infile:

                    #dup_treated=False
                    #logger_merge.info('Line : %s',line.strip())

                    #if line =='\n' or line.startswith('#') or line.startswith('@'):
                    #    outfile.write(line)
                    #else :
                    #    updated_line=line
                    #    for dup in occ_dup:
                    #        if  re.search(r'\b' + re.escape(dup[0]) + r'\b', line) \
                    #            and (dup[1]>remain_occ):
                    #            updated_line = updated_line.replace\
                    #            (dup[0],f'{dup[0]}_extra_node_{nbr_file_treated}')
                    #            logger_merge.info('dup %s',dup)
                    #            logger_merge.info('remain_occ %s',remain_occ)
                    #            logger_merge.info('updated_line %s',updated_line.strip())
                    #            logger_merge.info('file : %s',infile)
                    #            dup_treated_list.append(dup)
                    #            dup_treated=True

                    #    if dup_treated is True :
                    #        outfile.write(updated_line)
                    #    else :
                    #        outfile.write(line)

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
            print('Number of file treated : %s',nbr_file_treated)

        all_new_ttl_files = [f for f in Path(f'{path_duplicate_treated}/{remain_occ}')\
            .iterdir() if f.is_file()]

        # merge files in an only one file
        merge_graph(all_new_ttl_files,path_merged,remain_occ)

        #merged_file=f'{path_merged}/merged_graph_{remain_occ}.ttl'
        #with open(merged_file, 'w', encoding='utf-8') as m_file:
        #    for file in all_new_ttl_files: # Open each input file in read mode
        #        with open(file, 'r', encoding='utf-8')\
        #         as ttl_file: # Read the content and write it to the output file
        #            content = ttl_file.read()
        #            m_file.write(content)
        #            m_file.write('\n')  # Adds a newline between files

        remain_occ = remain_occ + 1
    return all_new_ttl_files

def merge_graph(all_new_ttl_files,path_merged,remain_occ):
    ''' placeholder function to indicate graph merging is done '''
    merged_file=f'{path_merged}/merged_graph_{remain_occ}.ttl'
    with open(merged_file, 'w', encoding='utf-8') as m_file:
        for file in all_new_ttl_files: # Open each input file in read mode
            with open(file, 'r', encoding='utf-8')\
             as ttl_file: # Read the content and write it to the output file
                content = ttl_file.read()
                m_file.write(content)
                m_file.write('\n')  # Adds a newline between files
    print('Graphs have been merged successfully.')

def max_node_occ_value(path_files,homonymes_nodes,logger_homonymes):
    '''return the node that have the max occurrence'''

    occ_dup=occurence_duplicate(homonymes_nodes,path_files)

    if occ_dup != []:
        print(f'List of all the nodes that appeared in several ttl files : {occ_dup} ')
        logger_homonymes.info('List of all the nodes that appeared in several ttl files : %s'\
                              ,occ_dup)
        m_n_o_v = max(sublist[1] for sublist in occ_dup)
        print('Max number of occurence of nodes in ttl files:', m_n_o_v)
        logger_homonymes.info('Max number of occurence of nodes in ttl files : %s', m_n_o_v)
        node_max_occ=[sublist[0] for sublist in occ_dup if sublist[1] == m_n_o_v]
        print('Node that have the max number of occurence in ttl files :',node_max_occ)
        logger_homonymes.info('Node that have the max number of occurence in ttl files : %s'\
                              ,node_max_occ)

    else:
        print('NO DUPLICATES NODES FOUND')
        node_max_occ='NULL'
        m_n_o_v = 0

    return m_n_o_v, node_max_occ
