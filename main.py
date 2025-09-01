'''main.py'''

import argparse
from pathlib import Path
import os
import shutil
import datetime
import subprocess
from generate_ttl_files.generate_ttl import generate_ttl
#from merge_ttl_files.merge_ttl import merge_ttl
from merge_ttl_files.utils.utils_merge import max_node_occ_value


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("nbrttl", help="number of ttl file to generate")
    args = parser.parse_args()

    path=Path(f'{os.getcwd()}')
    path_gen=Path(f'{path}/generate_ttl_files')
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    ### Choose the model to use ####
    model_list = []
    FILE_MODEL = f'{path_gen}/model/models.txt'
    with open(FILE_MODEL, mode='r',encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            cleaned_line = line.strip()
            model_list.append(cleaned_line)
    model = model_list[5]

    PATH_RESULT = f'{path}/results/synthetics_graphs/{date}/{model}'
    PATH_MERGED = f'{PATH_RESULT}/merged_graph'

    #path_result=f'{path}/merged_graph'

    #subprocess.run(['clear'],check=True)

    print('TTL FILE GENERATION IS IN PROGRESS')

    ONTOLOGY=generate_ttl(path_gen,PATH_RESULT,args.nbrttl,model)

    #save ttl file in another folder
    SAVED_TTL_FILES = Path(f'{Path(PATH_RESULT)}/saved_ttl_files')
    SAVED_TTL_FILES.mkdir(parents=True, exist_ok=True)

    #remove previous files
    for file in SAVED_TTL_FILES.iterdir():
        if file.is_file():
            file.unlink()

    for file in Path(PATH_RESULT).iterdir():
        if file.is_file():
            shutil.copy2(file, SAVED_TTL_FILES / file.name)

    print(f'\nTTL FILES ARE STORED IN : {PATH_RESULT}\n')
    print('#### TTL FILE GENERATION PROCESS ENDED ####\n')

    print('MERGING TTL FILE PROCESS IS IN PROGRESS\n')

    #remove old files in the merge folfer
    if Path(PATH_MERGED).exists() and Path(PATH_MERGED).is_dir():
        for files in Path(PATH_MERGED).iterdir():
            if files.is_file():
                files.unlink()

    # find max number of duplicates nodes
    max_node_occ_value = max_node_occ_value(PATH_RESULT,ONTOLOGY)

    print('max_node_occ_value:', max_node_occ_value)

    nbr_occ_max=max_node_occ_value[0]
    node_max_occ=max_node_occ_value[1]

    print('max_node_occ_value',max_node_occ_value)

    if max_node_occ_value[1] != 'NULL':
        print(f'\nNode {node_max_occ} appears {nbr_occ_max} times in {nbr_occ_max} different TTL files\n')
        #print(nbr_occ_max)

        #REMAIN_OCC=0

        #while REMAIN_OCC != nbr_occ_max + 1:
        #merge_ttl(PATH_RESULT,PATH_MERGED,ONTOLOGY,nbr_occ_max)
        #    REMAIN_OCC=REMAIN_OCC+1
        #merge_ttl(PATH_RESULT,PATH_MERGED,0,ONTOLOGY)

        #print('#### MERGING PROCESS ENDED ####\n')
        #print(f'MERGED FILES ARE STORED in : {PATH_RESULT} \n')

    #else:
        #print('#### MERGING PROCESS ENDED ####\n')
        #print('NO DUPLICATES NODES FOUND\n')
        #path_result=merge_ttl(TTL_FOLDER,0,ONTOLOGY)
