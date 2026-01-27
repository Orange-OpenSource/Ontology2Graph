# Software Name : Ontologie2Graph
# SPDX-FileCopyrightText: Copyright (c) Orange SA
# SPDX-License-Identifier: BSD-4-Clause
#
# This software is distributed under the BSD 4-Clause "Original" or "Old" License,
# see the "LICENSE" file for more details or <license-url>

'''
This script generates knowledge graphs in turtle format based on an ontology schema and a prompt.
Please read the following. 
    - You just have to pass the number of graph you want as an argument of this script.
    - "model_nbr" and "prompt_type" must be set directly in this script before launching.
    - You have to refer to utils_gen/models/models.json to set "model_nbr".
    - You have to refer to utils_gen/prompts/prompts.json to set "prompt_type".
    - The generated ttl files are stored in the results/synthetics_graphs folder.
    - If you use an API, make sure "LLM_PROXY_KEY" environment variable is set with your API key.
    - This script also creates a logs files containing some information about the generation.
    - This script must be launch from the generate_ttl_files folder where it is stored

Usage:
    python generate_ttl.py --nbrttl <number of ttl file to generate>

Arguments:
    nbrttl : Number of graph (ttl file to generate)    
'''
import logging
import os
import datetime
from pathlib import Path
from utils_gen import utils as utils_gen
from utils_common import utils as utils_common

### set argument parser ###
args = utils_common.setup_argument_parser([("nbrttl", "number of ttl file to generate")])

### choose the model to use ####
model_name = utils_gen.model_to_choose(model_nbr=7)

### set the prompt type ###
PROMPT_TYPE="4_1_AI_enhance_manually"

### build folders & files paths ###
PATH_RESULT, BAD_PATH_RESULT, MISFORMATED_PATH, ONTOLOGY_FILE, PROMPT_FILE, PATH_GRAPH, TEMP_FILE,\
LOG_FILE, PATH_MERGED = utils_gen.build_folder_paths_and_files(model_name)

### Setup logger ###
logger_gen= utils_common.setup_logger(LOG_FILE,'gen_log',logging.INFO)

NUMBER_OF_GRAPH = 0
ONTO_NAME=Path(ONTOLOGY_FILE).stem
NBR_TTL_INT = int(args.nbrttl)

### remove old files in the result folder ###
utils_gen.remove_file_in_folder(PATH_RESULT)
utils_gen.remove_file_in_folder(BAD_PATH_RESULT)

os.system("clear")
print('TTL FILE GENERATION IS IN PROGRESS')

### Generate graphs ###
while NUMBER_OF_GRAPH != int(NBR_TTL_INT):

    ### query llm ##
    response=utils_gen.query_llm(ONTOLOGY_FILE,PROMPT_FILE,model_name,PROMPT_TYPE)

    logger_gen.info('Graph generation with prompt type : %s',{PROMPT_TYPE})

    ### build file name for each graph ###
    date_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    FILE_RESULT = f'{PATH_RESULT}/{PROMPT_TYPE}_{date_time}_{ONTO_NAME}.ttl'
    BAD_FILE_RESULT = f'{BAD_PATH_RESULT}/{PROMPT_TYPE}_{date_time}_{ONTO_NAME}_BAD.ttl'

    ### Store results and logs some infos ###
    utils_gen.storing_results(response,TEMP_FILE,FILE_RESULT,logger_gen,model_name)

    NUMBER_OF_GRAPH += 1
    print(f'\nNUMBER OF GRAPH GENERATED : {NUMBER_OF_GRAPH}\n')
    print("Sleeping 60 sec to reset the context")
    #time.sleep(60)
    print("Awake !")

### re format TTL files if needed ###
utils_gen.format_ttl(PATH_RESULT,MISFORMATED_PATH,logger_gen)

### Check Turtle syntax and log some info ###
utils_common.check_ttl(PATH_RESULT,BAD_PATH_RESULT,logger_gen)

### remove old files in the merge folder ###
utils_gen.remove_file_in_folder(PATH_MERGED)

print(f'\nTTL FILES ARE STORED IN : {PATH_RESULT}\n')
print(f'LOGS FILES ARE STORED IN : {LOG_FILE}\n')

print('#### TTL FILE GENERATION PROCESS ENDED ####\n')
