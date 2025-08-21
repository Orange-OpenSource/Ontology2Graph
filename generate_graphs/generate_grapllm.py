""" This python script generates knowledge graph in turtle format based on an ontology schema, a 
prompt and/or a graph example. It uses the internal Orange LLM Proxy portal 
(https://portal.llmproxy.ai.orange/) for which you must have an account. You just have to pass
the number of graph you want as an argumet. Several constant must be set directly in this script 
before launching
"""
import os
import sys
import datetime
from pathlib import Path
from utils.utils_gen import query_llm, storing_results, check_ttl

## SET constant ##

# PATH constant where are stored the needed ressources, prompt, ontology and graph
PATH=Path(f'{os.getcwd()}')
#PATH=f'{os.getcwd()}/DIGITAL_TWIN/gengraphllm' # when using crontab
PATH_ONTOLOGY=f'{PATH}/ontologies'
PATH_PROMPT=f'{PATH}/prompts'
PATH_GRAPH=f'{PATH}/graph'

## PROMPT_TYPE to choose ##
PROMPT_TYPE='First_prompt'
#PROMPT_TYPE='Second_prompt'
#PROMPT_TYPE='Third_prompt'

## ONTOLOGY to choose ##
ONTO='Noria'
#ONTOLOGY='pygraph'

## choose MODEL ##
FILE_MODEL = f'{PATH}/model/models.txt'
model_list = []
# Open the text file
with open(FILE_MODEL, mode='r',encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        cleaned_line = line.strip()
        model_list.append(cleaned_line)
    file.close

MODEL=model_list[5]
DATE = datetime.datetime.now().strftime("%Y-%m-%d")

PATH_RESULT=f'{PATH.parent}/results/synthetics_graphs/{DATE}/{MODEL}'
BAD_PATH_RESULT=f'{PATH_RESULT}/Bad_Turtle_Syntax'
TEMP_FILE=f'{PATH_RESULT}/temp.ttl'

with open(f'{PATH_ONTOLOGY}/Noria.ttl','rt',encoding='utf-8') as ontology:
    ONTOLOGY = ','.join(str(x) for x in ontology.readlines())
    ontology.close

with open(f'{PATH_PROMPT}/{PROMPT_TYPE}.txt','rt',encoding='utf-8') as prompt:
    PROMPT = ','.join(str(x) for x in prompt.readlines())
    prompt.close

# Only for second and third prompt
#with open(f'{PATH_GRAPH}/full_graph.ttl','rt',encoding='utf-8') as graph:
#    GRAPH = ','.join(str(x) for x in graph.readlines())
#    graph.close

os.makedirs(f'{PATH_RESULT}/', exist_ok=True)
os.makedirs(f'{BAD_PATH_RESULT}', exist_ok=True)

arg = sys.argv[1:]
TARGET_NUMBER_OF_GRAPH = int(arg[0])
NUMBER_OF_GRAPH = 0

## Generate graphs ##

while NUMBER_OF_GRAPH != TARGET_NUMBER_OF_GRAPH:

    DATE_TIME = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    FILE_RESULT=f'{PATH_RESULT}/{PROMPT_TYPE}_{DATE_TIME}_{ONTO}.ttl'
    BAD_FILE_RESULT=f'{BAD_PATH_RESULT}/{PROMPT_TYPE}_{DATE_TIME}_{ONTO}_BAD.ttl'

    #Query LLM
    response=query_llm(DATE_TIME,PROMPT,ONTOLOGY,MODEL)

    #Store results
    storing_results(response,TEMP_FILE,FILE_RESULT)

    # Check Turtle syntax
    check_ttl(FILE_RESULT,BAD_FILE_RESULT, BAD_PATH_RESULT,0)

    NUMBER_OF_GRAPH += 1
    print(PATH_RESULT)
