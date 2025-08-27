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

def check_ttl(file_result, bad_file_result, bad_path_result,merged):
    '''check ttl syntax and store wrong file in specific folder'''
    command=["ttl",file_result]
    ttlvalidator=subprocess.Popen(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    stdout, stderr = ttlvalidator.communicate()
    if merged==1:
        print(f'Merged graph : Turtle validator Result: {stdout},{stderr}')
    else:
        print(f'Turtle validator Result: {stdout}, {stderr}')

    if stdout!='Validator finished with 0 warnings and 0 errors.\n' :
    # move bad file in bad folder and Save logs

        os.makedirs(f'{bad_path_result}', exist_ok=True)
        shutil.move(file_result, bad_file_result)

        with open(f'{bad_path_result}/errors.log', 'a',encoding='utf-8') as log:
            log.write(f'{bad_file_result} : {ttlvalidator.communicate()}\n')
            log.close()

def get_last_folder_part(string, sep_char):
    """get last part of a folder string"""
    string_parts=string.split(sep_char)
    last_part=string_parts[len(string_parts)-1]
    if last_part=='':
        last_part=string_parts[len(string_parts)-2]
    return last_part

def remove_duplicate_prefix(output_file_temp,merged_file):
    '''remove duplicate prefix of the merged file'''
    nodes_lines=[]
    prefix_lines=[]
    prefix_lines_unique=[]

    with open (output_file_temp, 'r', encoding='utf-8') as outfile:
        lines = outfile.readlines()
        prefix_lines = [lines for lines in lines if lines.startswith('@')]
        nodes_lines= [lines for lines in lines if not lines.startswith('@')]
        outfile.close()

    os.remove(output_file_temp)

    #remove duplicate prefix
    for item in prefix_lines:
        if item not in prefix_lines_unique:
            prefix_lines_unique.append(item)

    with open (merged_file, 'w', encoding='utf-8') as graph:
        graph.writelines(prefix_lines_unique)
        graph.writelines(nodes_lines)
        graph.close()

def find_duplicates_nodes(path,ontology):
    '''find duplicates nodes in ttl files, just add the folder where the files
    are stored as an argument'''

    #List all the ttl graph files in PATH except folder
    all_files = [f.name for f in Path(path).iterdir() if f.is_file()]

    #datatypeproperties=retreive_datatype_properties(ontology)
    #print('DTP ///', datatypeproperties)

    #rebuild complete file path (folder/file)
    for i, file in enumerate(all_files):
        all_files[i]= f'{path}/{file}'
    
    print('all_file',all_files)
    
    #print(all_files)

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
                                and (pred != rdfs.isDefinedBy)):
                #print(subj, pred, obj)
                nx_graph.add_edge(str(subj), str(obj), label=str(pred))

        nodes=list(nx_graph.nodes)
        all_nodes.append(nodes)

        #print('all_nodes',all_nodes)

    #transform list of list into a simple list
    all_nodes_list = [item for sublist in all_nodes for item in sublist]

    #all_nodes_list_unique = list(set(all_nodes_list))
    #print(f'NODES OF FINAL GRAPH : {all_nodes_list_unique} \n')

    counts=Counter(all_nodes_list)
    dupplicate_nodes=[item for item, count in counts.items() if count > 1]
    #print(f'NODE WITH DUPLICATE IN THE GENERATED GRAPH: {dupplicate_nodes} \n ' )
    print(dupplicate_nodes)

    return dupplicate_nodes

def occurence_duplicate(duplicates_nodes,path):
    '''compute the occurence of duplicates all over the ttl files once a node appear in a ttl file
    occu_duplicates is increased by 1'''
    occu_duplicates=[[duplicates_nodes[i],0] for i in range(0,len(duplicates_nodes))]

    #List all the ttl graph files in PATH except folder
    all_files = [f.name for f in Path(path).iterdir() if f.is_file()]

    #rebuild complete file path (folder/file)
    for i, file in enumerate(all_files):
        all_files[i]= f'{path}/{file}'

    for file in all_files:

        with open(file,'r',encoding='utf-8') as file:
            content = file.read()

        for item in occu_duplicates:
            if item[0] in content:
                item[1]=item[1]+1

        file.close()
    #print('occu_duplicates_final',occu_duplicates)
    return occu_duplicates

def rename_duplicates_nodes(path,duplicates_nodes,nbr_occ):
    '''rename the duplicates nodes based on nbr_occ. if 10 nodes have the same name in all the 
    graphs generated and nbr_occ=2, 2 nodes will keep the same name and 8 nodes will be renamed'''

    #List all the ttl graph files in PATH except folder
    all_files = [f.name for f in Path(path).iterdir() if f.is_file()]

    #rebuild complete file path (folder/file)
    for i, file in enumerate(all_files):
        all_files[i]= f'{path}/{file}'

    occ_dup=occurence_duplicate(duplicates_nodes,path)
    #print(f'occ_dup : {occ_dup}')

    for i,dup in enumerate(occ_dup):

        j=0
        for ttl_file in all_files :

            with open(ttl_file,'r',encoding='utf-8') as file:
                content = file.read()
                file.close()

                if  (dup[0] in content) and (dup[1] > nbr_occ):
                    #print(dup)
                    new_node=f'{dup[0]}_extra_node_{j}'
                    #print(new_node)
                    occ_dup[i][1]=occ_dup[i][1]-1
                    #print(f'{dup} \n')

                    #update content
                    content=content.replace(dup[0],new_node)

                    new_node=''
                    j=j+1

                    with open(ttl_file, 'w',encoding='utf-8') as file:
                        file.write(content)
                        file.close()

def max_node_occ_value(ttl_folder,ontology):
    '''return the max occurence of nodes'''

    duplicate_nodes=find_duplicates_nodes(ttl_folder,ontology)
    print('dup',duplicate_nodes)

    occ_dup=occurence_duplicate(duplicate_nodes,ttl_folder)
    print(occ_dup)

    return max(sublist[1] for sublist in occ_dup)
