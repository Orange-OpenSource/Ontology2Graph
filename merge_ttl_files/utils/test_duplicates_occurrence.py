'''compute nodes occurence in ttl files, requires files location and ontology
location as arguments. To be use with file in llm_graphs_dup_treated folder'''

import argparse
import os
from pathlib import Path
import logging
from utils_merge import find_duplicates_nodes,occurence_duplicate

parser = argparse.ArgumentParser()
parser.add_argument("path")
parser.add_argument("ontology")
args = parser.parse_args()

path=args.path
ontology=args.ontology

REMAIN_OCC=int(Path(path).name)

#set logger
test_dup_log_file=Path(f'{Path(path).parent}/test_{REMAIN_OCC}_.log')
if test_dup_log_file.is_file():
    os.remove(test_dup_log_file)

logger_test = logging.getLogger('test_duplicate')
handler = logging.FileHandler(test_dup_log_file)
logger_test.setLevel(logging.INFO)
logger_test.addHandler(handler)

os.system("clear")
PATH_GRAPH_LLM=f'{Path(path).parent.parent}/'
#logger_merge.info('path_graph_llm : ',PATH_GRAPH_LLM)

duplicates_nodes_llm=find_duplicates_nodes(PATH_GRAPH_LLM,ontology)

duplicates_nodes_treated=find_duplicates_nodes(path,ontology)

occ_dup_llm_graph=occurence_duplicate(duplicates_nodes_llm,PATH_GRAPH_LLM)
occ_dup_llm_graph_treated=occurence_duplicate(duplicates_nodes_treated,path)

logger_test.info('################### REMAIN OCC = %s ################### \n',REMAIN_OCC)

if not duplicates_nodes_treated:
    logger_test.info('No duplicates nodes detected in %s ',path)
else:
    logger_test.info('DUPLICATES NODES DETECTED in %s \n',path)
    logger_test.info('occurence_duplicate_llm_graph_treated %s \n',occ_dup_llm_graph_treated)
    logger_test.info('occurence duplicate nodes llm : %s \n',occ_dup_llm_graph)

    for dup_occ in occ_dup_llm_graph:
        #print(dup_occ)
        for dup_occ_treated in occ_dup_llm_graph_treated:

            if dup_occ[0]==dup_occ_treated[0]:
                logger_test.info('dup_occ (%s) ///// dup_occ_treated (%s)',dup_occ,dup_occ_treated)

                if dup_occ[1]==dup_occ_treated[1]:

                    if dup_occ_treated[1] == REMAIN_OCC:
                        logger_test.info('dup_occ_treated (%s) equal to REMAIN OCC (%s)\n',\
                            dup_occ_treated[1],REMAIN_OCC)

                    if dup_occ_treated[1] > REMAIN_OCC:
                        logger_test.info('###### WARNING ###### dup_occ_treated (%s) is higher' \
                        'than remain_occ (%s) \n',dup_occ_treated[1],REMAIN_OCC)
                        print('###### WARNING ###### dup_occ_treated (%s) is higher than' \
                        ' remain_occ (%s) \n',dup_occ_treated[1],REMAIN_OCC)

                    if dup_occ_treated[1]<REMAIN_OCC:
                        logger_test.info('dup_occ (%s) = dup_occ_treated (%s) because dup_occ is'\
                                          'lower than REMAIN_OCC (%s)\n',dup_occ[1],\
                                            dup_occ_treated[1],REMAIN_OCC)

                if dup_occ[1]>dup_occ_treated[1]:

                    if dup_occ_treated[1] == REMAIN_OCC:
                        logger_test.info('dup_occ_treated (%s) equal to remain occ (%s) ' \
                        ,dup_occ_treated[1],REMAIN_OCC)

                    if dup_occ_treated[1] > REMAIN_OCC:
                        logger_test.info('###### WARNING ###### dup_occ_treated (%s) is higher' \
                        ' than remain_occ (%s)',dup_occ_treated[1],REMAIN_OCC)
                        print('###### WARNING ###### dup_occ_treated (%s) is higher than' \
                        'remain_occ (%s)', dup_occ_treated[1],REMAIN_OCC)

                    if dup_occ_treated[1]<REMAIN_OCC:
                        logger_test.info('###### WARNING ###### dup_occ_treated (%s) is lower' \
                        ' than remain_occ (%s) but higher than dup_occ (%s)\n',dup_occ_treated[1] \
                            ,REMAIN_OCC,dup_occ[1])
                        print('###### WARNING ###### ',dup_occ_treated,' : dup_occ_treated ('\
                                ,dup_occ_treated[1],') is lower than remain_occ (',REMAIN_OCC,')'\
                                  'but higher than dup_occ (',dup_occ[1],')\n')

                if dup_occ[1]<dup_occ_treated[1]:

                    if dup_occ_treated[1] == REMAIN_OCC:
                        logger_test.info('###### WARNING ###### dup_occ_treated (%s) is equal to' \
                        ' remain occ (%s) but is higher than dup_occ (%s)',dup_occ_treated[1],\
                            REMAIN_OCC,dup_occ[1])
                        print('###### WARNING ###### dup_occ_treated (%s) is equal to remain occ' \
                        ' (%s) but is higher than dup_occ (%s)',dup_occ_treated[1],REMAIN_OCC,\
                            dup_occ[1])

                    if dup_occ_treated[1] > REMAIN_OCC:

                        logger_test.info('###### WARNING ###### %s : dup_occ_treated (%s) is' \
                        'higher than remain_occ (%s) and higher than dup_occ (%s)\n'\
                        ,dup_occ_treated,dup_occ_treated[1],REMAIN_OCC,dup_occ[1])

                        print('###### WARNING ######',dup_occ_treated,' : dup_occ_treated '\
                              '(',dup_occ_treated[1],') is higher than remain_occ (',REMAIN_OCC,')'\
                               'and higher than dup_occ (',dup_occ[1],')')

                    if dup_occ_treated[1]<REMAIN_OCC:

                        logger_test.info('###### WARNING ###### %s : dup_occ_treated (%s) is lower'\
                                         'than remain_occ (%s) but higher than dup_occ (%s)\n',\
                                         dup_occ_treated,dup_occ_treated[1],REMAIN_OCC,dup_occ[1])

                        print('###### WARNING ###### ',dup_occ_treated,' : dup_occ_treated ('\
                              ,dup_occ_treated[1],') is lower than remain_occ (',REMAIN_OCC,')'\
                                  'but higher than dup_occ (',dup_occ[1],')\n')

