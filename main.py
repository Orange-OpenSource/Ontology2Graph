'''main.py'''

import argparse
from generate_ttl_files.generate_ttl import generate_ttl
from merge_ttl_files.merge_ttl import merge_ttl
from merge_ttl_files.utils.utils_merge import max_node_occ_value


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("nbrttl", help="number of ttl file to generate")
    args = parser.parse_args()

    print('TTL FILE GENERATION IS IN PROGRESS')

    TTL_FOLDER, ONTOLOGY=generate_ttl(args.nbrttl)

    print(f'\nTTL files are stored in : \n{TTL_FOLDER}')

    print('\n MERGING TTL FILE PROCESS IS IN PROGRESS')

    # find max number of duplicates nodes

    m_n_o_v = max_node_occ_value(TTL_FOLDER,ONTOLOGY)

    while m_n_o_v != 0:
        merge_ttl(TTL_FOLDER,m_n_o_v)
        m_n_o_v = m_n_o_v-1

    path_result=merge_ttl(TTL_FOLDER,0)

    print('MERGING PROCESS ENDED \n')
    print(f'MERGED FILES ARE STORED in : {path_result} \n')
