'''main.py'''

import argparse
import subprocess
from generate_ttl_files.generate_ttl import generate_ttl
from merge_ttl_files.merge_ttl import merge_ttl
from merge_ttl_files.utils.utils_merge import max_node_occ_value


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("nbrttl", help="number of ttl file to generate")
    args = parser.parse_args()

    subprocess.run(['clear'],check=True)

    print('TTL FILE GENERATION IS IN PROGRESS')

    TTL_FOLDER, ONTOLOGY=generate_ttl(args.nbrttl)

    print(f'\nTTL FILES ARE STORED IN : {TTL_FOLDER}\n')
    print('#### TTL FILE GENERATION PROCESS ENDED ####\n')
    print('\nMERGING TTL FILE PROCESS IS IN PROGRESS\n')

    # find max number of duplicates nodes
    max_node_occ_value = max_node_occ_value(TTL_FOLDER,ONTOLOGY)

    #print('max_node_occ_value:', max_node_occ_value)

    nbr_occ_max=max_node_occ_value[0]
    node_max_occ=max_node_occ_value[1]

    if max_node_occ_value[1] != 'NULL':
        print(f'\nNode {node_max_occ} appears {nbr_occ_max} times in {nbr_occ_max} different TTL files\n')
        #print(nbr_occ_max)

        REMAIN_OCC=0

        while REMAIN_OCC != nbr_occ_max-1:
            merge_ttl(TTL_FOLDER,REMAIN_OCC,ONTOLOGY)
            REMAIN_OCC=REMAIN_OCC+1
        path_result=merge_ttl(TTL_FOLDER,0,ONTOLOGY)
        print('#### MERGING PROCESS ENDED ####\n')
        print(f'MERGED FILES ARE STORED in : {path_result} \n')
    else:
        print('#### MERGING PROCESS ENDED ####\n')
        print('NO DUPLICATES NODES FOUND\n')
        #path_result=merge_ttl(TTL_FOLDER,0,ONTOLOGY)
