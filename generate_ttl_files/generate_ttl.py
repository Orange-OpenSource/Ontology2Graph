''' This function generates knowledge graph in turtle format based on an ontology schema and a 
prompt. It uses the internal Orange LLM Proxy portal (https://portal.llmproxy.ai.orange/) 
Please read the following. 
    - You just have to pass the number of graph you want as an argument of this script.
    - Model_nbr must be set directly in this script before launching.
    - This script uses utils functions defined in utils_gen.py located in the utils folder.
    - The generated ttl files are stored in the results/synthetics_graphs folder.
    - Make sure you have set the LLM_PROXY_KEY environment variable with your API key.
    - This script also creates a log file containing some information about the generation.
    - The script sleeps 60 seconds between each generation to reset the context.
    - Make sure you have installed the required packages listed in the requirements.txt file.
    - To run the script, use the command: python generate_ttl.py <number_of_ttl_files_to_generate>
    - This srcript must be launch from the generate_ttl_files folder where it is stored
'''

import argparse
import logging
import os
import datetime
import time
from pathlib import Path
from utils.utils_gen import query_llm, storing_results, check_ttl,\
    remove_file_in_folder, model_to_choose, build_folder_paths_and_files,\
    prompt_type_and_ontology_name, log

### set argument parser ###
parser = argparse.ArgumentParser()
parser.add_argument("nbrttl", help="number of ttl file to generate")
args = parser.parse_args()

### Choose the model to use ####
model = model_to_choose(model_nbr=7)

### build FOLDER PATHS & FILES ###
PATH_RESULT, BAD_PATH_RESULT, PATH_ONTOLOGY, PATH_PROMPT, PATH_GRAPH, TEMP_FILE,\
LOG_FILE, PATH_MERGED = build_folder_paths_and_files(model)

### Set up logger ###
remove_file_in_folder(Path(LOG_FILE).parent)
logger_gen = logging.getLogger('Gen_log')
handler_gen = logging.FileHandler(Path(LOG_FILE))
logger_gen.setLevel(logging.INFO)
logger_gen.addHandler(handler_gen)

## set PROMPT_TYPE and ontology ##
PROMPT_TYPE, ONTO_NAME=prompt_type_and_ontology_name()

with open(f'{PATH_ONTOLOGY}/Noria.ttl','rt',encoding='utf-8') as ontol:
    ONTOLOGY = ','.join(str(x) for x in ontol.readlines())

with open(f'{PATH_PROMPT}/{PROMPT_TYPE}.txt','rt',encoding='utf-8') as prpt:
    PROMPT = ','.join(str(x) for x in prpt.readlines())

NUMBER_OF_GRAPH = 0
NBR_TTL_INT = int(args.nbrttl)

### remove old files in the result folder ###
remove_file_in_folder(PATH_RESULT)
remove_file_in_folder(BAD_PATH_RESULT)

os.system("clear")
print('TTL FILE GENERATION IS IN PROGRESS')
logger = logging.getLogger('Gen_log')

## Generate graphs ##
while NUMBER_OF_GRAPH != NBR_TTL_INT:

    ### build file name for each graph ###
    date_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    FILE_RESULT = f'{PATH_RESULT}/{PROMPT_TYPE}_{date_time}_{ONTO_NAME}.ttl'
    BAD_FILE_RESULT = f'{BAD_PATH_RESULT}/{PROMPT_TYPE}_{date_time}_{ONTO_NAME}_BAD.ttl'

    # Query LLM
    response=query_llm(PROMPT,ONTOLOGY,model)

    # Store results
    storing_results(response,TEMP_FILE,FILE_RESULT)

    # Check Turtle syntax
    TTL_VALIDATOR_OUTPUT = check_ttl(FILE_RESULT,BAD_FILE_RESULT,BAD_PATH_RESULT,0)

    # log some info
    log(FILE_RESULT, BAD_FILE_RESULT, TTL_VALIDATOR_OUTPUT,response,model,logger_gen)

    NUMBER_OF_GRAPH += 1
    print(f'\nNUMBER OF GRAPH GENERATED : {NUMBER_OF_GRAPH}\n')
    print("Sleeping 60 sec to reset the context")
    time.sleep(60)
    print("Awake !")

### remove old files in the merge folder ###
remove_file_in_folder(PATH_MERGED)

print(f'\nTTL FILES ARE STORED IN : {PATH_RESULT}\n')
print('#### TTL FILE GENERATION PROCESS ENDED ####\n')
