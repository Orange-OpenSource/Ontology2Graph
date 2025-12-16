''' This function generates knowledge graph in turtle format based on an ontology schema and a 
prompt. It uses the internal Orange LLM Proxy portal (https://portal.llmproxy.ai.orange/) 
Please read the following. 
    - You just have to pass the number of graph you want as an argument of this script.
    - "model_nbr" vatriable must be set directly in this script before launching.
    - This script uses utils functions defined in utils_gen.py located in the utils folder.
    - The generated ttl files are stored in the results/synthetics_graphs folder.
    - Make sure you have set the LLM_PROXY_KEY environment variable with your API key.
    - This script also creates a log file containing some information about the generation.
    - The script sleeps 60 seconds between each generation to reset the context.
    - Make sure you have installed the required packages listed in the requirements.txt file.
    - To run the script, use the command: python generate_ttl.py <number_of_ttl_files_to_generate>
    - This srcript must be launch from the generate_ttl_files folder where it is stored'''

import time
import os
import datetime
from pathlib import Path
import utils_gen.utils as utils_gen
import utils_common.utils as utils_common

### set argument parser ###
args = utils_common.setup_argument_parser("parser", [("nbrttl", "number of ttl file to generate")])

### Choose the model to use ####
model = utils_gen.model_to_choose(model_nbr=7)

### Build FOLDERS & FILES PATHS ###
PATH_RESULT, BAD_PATH_RESULT, ONTOLOGY_FILE, PROMPT_FILE, PATH_GRAPH, TEMP_FILE,\
LOG_FILE, PATH_MERGED = utils_gen.build_folder_paths_and_files(model)

### Setup logger ###
utils_common.remove_file_in_folder(Path(LOG_FILE).parent)
logger= utils_common.setup_logger(LOG_FILE,'Gen_log')

NUMBER_OF_GRAPH = 0
ONTO_NAME=Path(ONTOLOGY_FILE).stem
NBR_TTL_INT = int(args.nbrttl)

### remove old files in the result folder ###
utils_common.remove_file_in_folder(PATH_RESULT)
utils_common.remove_file_in_folder(BAD_PATH_RESULT)

os.system("clear")
print('TTL FILE GENERATION IS IN PROGRESS')

## Generate graphs ##
while NUMBER_OF_GRAPH != int(NBR_TTL_INT):

    ### Query LLM ##
    response,PROMPT_TYPE=utils_gen.query_llm(ONTOLOGY_FILE,PROMPT_FILE,model)

    ### build file name for each graph ###
    date_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    FILE_RESULT = f'{PATH_RESULT}/{PROMPT_TYPE}_{date_time}_{ONTO_NAME}.ttl'
    BAD_FILE_RESULT = f'{BAD_PATH_RESULT}/{PROMPT_TYPE}_{date_time}_{ONTO_NAME}_BAD.ttl'

    ### Store results and logs some infos ###
    utils_gen.storing_results(response,TEMP_FILE,FILE_RESULT,logger,model)

    ### Check Turtle syntax and log some info ###
    utils_gen.check_ttl(FILE_RESULT,BAD_FILE_RESULT,BAD_PATH_RESULT,0,logger)

    NUMBER_OF_GRAPH += 1
    print(f'\nNUMBER OF GRAPH GENERATED : {NUMBER_OF_GRAPH}\n')
    print("Sleeping 60 sec to reset the context")
    time.sleep(60)
    print("Awake !")

### remove old files in the merge folder ###
utils_common.remove_file_in_folder(PATH_MERGED)

print(f'\nTTL FILES ARE STORED IN : {PATH_RESULT}\n')
print('#### TTL FILE GENERATION PROCESS ENDED ####\n')
