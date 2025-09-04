'''list of function to be used '''

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
    
    while count != nbr_file + 1:
    
        merged_file_list = [f.name for f in Path(path_merged).iterdir() if f.is_file()]
        print(merged_file_list)
        merged_file=f'{path_merged}/{merged_file_list[0]}'

        command=["ttl",merged_file]
        ttlvalidator=subprocess.Popen(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        stdout, stderr = ttlvalidator.communicate()
        if merged==1:
            print(f'Merged graph {Path(merged_file).name} : Turtle validator Result: {stdout},{stderr}\n')
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

def remove_duplicate_prefix(path_merged):
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

    #List all the ttl graph files in PATH except folder
    all_files = [f.name for f in Path(path).iterdir() if f.is_file()]

    datatypeproperties=retreive_datatype_properties(ontology)
    #print('DTP ///', datatypeproperties)

    #rebuild complete file path (folder/file)
    for i, file in enumerate(all_files):
        all_files[i]= f'{path}/{file}'

    all_nodes=[]
    nodes=[]
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

    for file in all_files :

        g = rdflib.Graph()
        g.parse(file, format="turtle")

        nx_graph = nx.DiGraph()

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

            if (isinstance(subj, URIRef) and isinstance(obj, URIRef) and (pred != rdf.type)
                                and (pred != rdfs.isDefinedBy) and pred not in datatypeproperties):
                #print(subj, pred, obj)
                nx_graph.add_edge(str(subj), str(obj), label=str(pred))

        nodes=list(nx_graph.nodes)
        nodes_with_bracket = [f"<{nodes}>" for nodes in nodes]
        all_nodes.append(nodes_with_bracket)

        #print('all_nodes',all_nodes)

    #transform list of list into a simple list
    all_nodes_list = [item for sublist in all_nodes for item in sublist]

    #all_nodes_list_unique = list(set(all_nodes_list))
    #print(f'NODES OF FINAL GRAPH : {all_nodes_list_unique} \n')

    counts=Counter(all_nodes_list)
    dupplicate_nodes=[item for item, count in counts.items() if count > 1]
    print('duplicate_nodes',dupplicate_nodes)
    #print(f'NODE WITH DUPLICATE IN THE GENERATED GRAPH: {dupplicate_nodes} \n ' )

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
            if item[0] in content:
                item[1]=item[1]+1

        file.close()
    return occu_duplicates

def rename_duplicates_nodes(path_result,path_merged,duplicates_nodes,nbr_occ_max):
    '''rename the duplicates nodes based on rename_step. if 10 nodes have the same name in all the 
    graphs generated and rename_step=2, 2 nodes will keep the same name and 8 nodes will 
    be renamed'''

    #duplicates_nodes = find_duplicates_nodes(path_result,ontology)
    occ_dup=occurence_duplicate(duplicates_nodes,path_result)

    print('occ_dup',occ_dup)
    all_ttl_files = [f.name for f in Path(path_result).iterdir() if f.is_file()]
    print(all_ttl_files)

    os.makedirs(Path(path_merged),exist_ok=True)
    os.makedirs(f'{Path(path_result)}/ttl_file_without_dup',exist_ok=True)

    path_ttl_file_without_dup=f'{Path(path_result)}/ttl_file_without_dup'

    remain_occ=0

    while remain_occ != int(nbr_occ_max) + 1:
        treated_ttl_file_index=0
        nbr_file_treated=0
        nbr_file_to_treat=int(nbr_occ_max)-int(remain_occ)

        for ttl_file in all_ttl_files :

            #treated_line=[]
            treated_ttl_file_index=treated_ttl_file_index+1

            print(f'\n### REMAIN OCC ### = {remain_occ}, nbr_occ_max = {nbr_occ_max}')
            print('#### FILE ####:', ttl_file)

            os.makedirs(Path(f'{path_ttl_file_without_dup}/{remain_occ}'),exist_ok=True)

            with open(Path(path_result)/ttl_file,'r',encoding='utf-8') as infile, \
                open(f'{Path(path_ttl_file_without_dup)}/{remain_occ}/New_{remain_occ}_{ttl_file}',\
                    'w',encoding='utf-8') as outfile:

                print('treated_ttl_file_index',treated_ttl_file_index)
                for line in infile:
                    dup_treated=False
                    print(line)
                    for dup in occ_dup:

                        if (dup[0] in line) and (nbr_file_treated < nbr_file_to_treat):

                            print("count",nbr_file_treated)
                            print('nbr_file_to_treat',nbr_file_to_treat)
                            updated_line = line.replace\
                                (dup[0],f'{dup[0][:-1]}_extra_node_{treated_ttl_file_index}>')

                            outfile.write(updated_line)
                            print('updated_line',updated_line.strip())
                            #treated_line.append(line)
                            print(updated_line)
                            dup_treated=True

                    if dup_treated is False or line=='\n':
                        outfile.write(line)
                        print(line)
                    #    treated_line.append(line)

            if dup_treated is True:
                nbr_file_treated=nbr_file_treated+1
                print("count",nbr_file_treated)
                print('nbr_file_to_treat',nbr_file_to_treat)
                #print(treated_line)

        os.makedirs(Path(f'{path_merged}'),exist_ok=True)
        ttl_file_folder=Path(f'{path_result}/ttl_file_without_dup/{remain_occ}')

        all_new_ttl_files = [f for f in  ttl_file_folder.iterdir() if f.is_file()]

        # merge mofified ttl file in an only one file
        merged_file=f'{path_merged}/merged_graph_{remain_occ}.ttl'
        print(merged_file)
        with open(merged_file, 'w', encoding='utf-8') as m_file:
            for file in all_new_ttl_files:
            # Open each input file in read mode
                with open(file, 'r', encoding='utf-8')\
                 as ttl_file:
                    # Read the content and write it to the output file
                    content = ttl_file.read()
                    m_file.write(content)
                    #m_file.write(f'{Path(file)}')
                    m_file.write('\n')  # Adds a newline between files

        remain_occ = remain_occ + 1

        # restore ttl files not mofified

        #saved_ttl_files=f'{Path(path_result)}/saved_ttl_files'

        #for file in Path(saved_ttl_files).iterdir():
        #    if file.is_file():
        #        shutil.copy2(file, Path(saved_ttl_files).parent / file.name)

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
        #print('NO DUPLICATES NODES FOUND')
        node_max_occ='NULL'
        m_n_o_v = 0

    return m_n_o_v, node_max_occ
