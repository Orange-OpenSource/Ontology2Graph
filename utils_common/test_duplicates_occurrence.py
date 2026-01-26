

import argparse
import os
from pathlib import Path
import logging
from merge_ttl_files.utils_merge import find_duplicates_nodes,occurence_duplicate

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

duplicates_nodes_llm=find_duplicates_nodes(PATH_GRAPH_LLM,ontology)
duplicates_nodes_treated=find_duplicates_nodes(path,ontology)

occ_dup_llm_graph=occurence_duplicate(duplicates_nodes_llm,PATH_GRAPH_LLM)
occ_dup_llm_graph_treated=occurence_duplicate(duplicates_nodes_treated,path)

node_max_occ_llm=node_max_occ_llm_treated=[]

if occ_dup_llm_graph != []:
    m_n_o_v_llm = max(sublist[1] for sublist in occ_dup_llm_graph)
    node_max_occ_llm=[sublist[0] for sublist in occ_dup_llm_graph if sublist[1] == m_n_o_v_llm]

if occ_dup_llm_graph_treated != []:
    m_n_o_v_llm_treated = max(sublist[1] for sublist in occ_dup_llm_graph_treated)
    node_max_occ_llm_treated = [sublist[0] for sublist in occ_dup_llm_graph_treated if\
                                     sublist[1] == m_n_o_v_llm_treated]

logger_test.info('################### REMAIN OCC = %s ################### \n',REMAIN_OCC)

if not duplicates_nodes_treated:
    logger_test.info('No duplicates nodes detected in %s ',path)
    print('\n NO DUPLICATED NODES DETECTED AFTER TREATEMENT FOR REMAIN_OCC = ',REMAIN_OCC)
    print(path,'\n')

else:
    logger_test.info('DUPLICATES NODES DETECTED in %s \n',path)
    logger_test.info('occurence duplicate nodes llm : %s \n',occ_dup_llm_graph)
    logger_test.info('Max node occurence before treatment : %s %s \n',node_max_occ_llm,m_n_o_v_llm)

    logger_test.info('occurence duplicate nodes llm after treatment %s \n',\
                     occ_dup_llm_graph_treated)
    logger_test.info('Max node occurence after treatment : %s %s \n',node_max_occ_llm_treated,\
                     m_n_o_v_llm_treated)

    PROBLEM=False

    for dup_occ in occ_dup_llm_graph:
        #print(dup_occ)
        for dup_occ_treated in occ_dup_llm_graph_treated:

            if dup_occ[0]==dup_occ_treated[0]:
                logger_test.info('\ndup_occ (%s) //// dup_occ_treated (%s)',dup_occ,dup_occ_treated)

                if dup_occ[1] == REMAIN_OCC:

                    if dup_occ_treated[1] == REMAIN_OCC:
                        logger_test.info('dup_occ_treated (%s) equal to REMAIN OCC (%s)',\
                                           dup_occ_treated[1],REMAIN_OCC)

                    if dup_occ_treated[1] > REMAIN_OCC:
                        logger_test.info('###### WARNING ###### dup_occ : (%s)',dup_occ)
                        logger_test.info('dup_occ_treated (%s) is higher than remain_occ (%s),'\
                                         ' should be equal to remain_occ',dup_occ_treated[1],\
                                            REMAIN_OCC)
                        print('\n###### WARNING ###### ',dup_occ_treated,' : dup_occ_treated (',\
                              dup_occ_treated[1],') is higher than remain_occ (',REMAIN_OCC,'),'\
                              ' should be equal to remain_occ')
                        PROBLEM=True

                    if dup_occ_treated[1] < REMAIN_OCC:
                        logger_test.info('###### WARNING ###### dup_occ : (%s)',dup_occ)
                        logger_test.info('dup_occ_treated (%s) is lower than remain_occ (%s),'\
                                         ' should be equal to remain_occ',dup_occ_treated[1],\
                                         REMAIN_OCC)
                        print('\n###### WARNING ###### ',dup_occ_treated,' : dup_occ_treated (',\
                              dup_occ_treated[1],') is lower than remain_occ (',REMAIN_OCC,'),'\
                              ' should be equal to remain_occ')
                        PROBLEM=True

                if dup_occ[1] > REMAIN_OCC:

                    if dup_occ_treated[1] == REMAIN_OCC:
                        logger_test.info('dup_occ_treated (%s) equal to remain occ (%s) ' \
                                          ,dup_occ_treated[1],REMAIN_OCC)

                    if dup_occ_treated[1] > REMAIN_OCC:
                        logger_test.info('###### WARNING ###### dup_occ : (%s)',dup_occ)
                        logger_test.info('dup_occ_treated (%s) is higher than remain_occ (%s),'\
                                         ' should be equal to remain_occ',dup_occ_treated[1],\
                                         REMAIN_OCC)
                        print('\n###### WARNING ###### ',dup_occ_treated,' : dup_occ_treated (',\
                              dup_occ_treated[1],') is higher than remain_occ (',REMAIN_OCC,'),'\
                              ' should be equal to remain_occ')
                        PROBLEM=True

                    if dup_occ_treated[1]<REMAIN_OCC:
                        logger_test.info('###### WARNING ###### dup_occ : (%s)',dup_occ)
                        logger_test.info('dup_occ_treated (%s) is lower than remain_occ (%s),'\
                                         ' should be equal to remain_occ', dup_occ_treated[1],\
                                         REMAIN_OCC)
                        print('\n###### WARNING ###### ',dup_occ_treated,' : dup_occ_treated (',\
                              dup_occ_treated[1],') is lower than remain_occ, (',REMAIN_OCC,'),'\
                              ' should be equal to remain_occ')
                        PROBLEM=True

                if dup_occ[1] < REMAIN_OCC:

                    if dup_occ_treated[1] == dup_occ[1]:
                        logger_test.info('As dup_occ (%s) is lower than remain_occ (%s),'\
                                         ' dup_occ_treated (%s) is equal to dup_occ (%s) '\
                                          ,dup_occ[1],REMAIN_OCC,dup_occ_treated[1],dup_occ[1])

                    if dup_occ_treated[1] == REMAIN_OCC:
                        logger_test.info('###### WARNING ###### dup_occ : (%s)',dup_occ)
                        logger_test.info('dup_occ_treated (%s) is equal to remain occ (%s),'\
                                         ' should be equal to dup_occ (%s)',dup_occ_treated[1],\
                                         REMAIN_OCC,dup_occ[1])
                        print('\n###### WARNING ###### ',dup_occ_treated,' : dup_occ_treated (',\
                              dup_occ_treated[1],') is equal to remain_occ (',REMAIN_OCC,'),'\
                              ' should be equal to dup_occ (',dup_occ[1],')')
                        PROBLEM=True

                    if dup_occ_treated[1] > REMAIN_OCC:
                        logger_test.info('###### WARNING ###### dup_occ : (%s)',dup_occ)
                        logger_test.info('dup_occ_treated (%s) is higher than remain_occ (%s),'\
                                         ' should be equal to dup_occ (%s)',dup_occ_treated[1]\
                                          ,REMAIN_OCC,dup_occ[1])
                        print('\n###### WARNING ###### ',dup_occ_treated,' : dup_occ_treated (',\
                              dup_occ_treated[1],') is higher than remain_occ (',REMAIN_OCC,'),'\
                              ' should be equal to dup_occ (',dup_occ[1],')')
                        PROBLEM=True

                    if dup_occ_treated[1] < REMAIN_OCC and dup_occ_treated[1] != dup_occ[1] :
                        logger_test.info('###### WARNING ###### dup_occ : (%s)',dup_occ)
                        logger_test.info('dup_occ_treated (%s) is lower than remain_occ (%s) and'\
                                         ' not equal to dup_occ (%s), should be equal to dup_occ\n'\
                                         ,dup_occ_treated,REMAIN_OCC,dup_occ[1])
                        print('\n###### WARNING ###### ',dup_occ_treated,' : dup_occ_treated (',\
                              dup_occ_treated[1],') is lower than remain_occ (',REMAIN_OCC,')'\
                              ' and not equal to dup_occ (',dup_occ[1],'), should be equal to'\
                              ' dupp_occ')
                        PROBLEM=True

    if PROBLEM is False:
        print('\nDUPLICATED NODES AFTER TREATMENT DETECTED FOR REMAIN_OCC=',REMAIN_OCC,\
              'WITHOUT ANY PROBLEM \n'\
              '\nSEE ',test_dup_log_file,' FOR MORE INFORMATION\n')

    else:
        print('\n PROBLEMS DETECTED SEE ',test_dup_log_file,' FOR MORE INFORMATION\n')
