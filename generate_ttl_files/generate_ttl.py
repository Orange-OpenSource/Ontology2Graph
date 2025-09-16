''' This function generates knowledge graph in turtle format based on an ontology schema, a prompt
    and/or a graph example. It uses the internal Orange LLM Proxy portal 
    (https://portal.llmproxy.ai.orange/) for which you must have an account. You just have to pass
    the number of graph you want as an argumet. Several constant must be set directly in this script 
    before launching'''

import argparse
import os
import datetime
from pathlib import Path

from generate_ttl_files.utils.utils_gen import query_llm, storing_results, check_ttl
#from utils.utils_gen import query_llm, storing_results, check_ttl

def generate_ttl(path_gen,path_result,nbr_ttl,model):
    '''function to generate ttl files'''

#parser = argparse.ArgumentParser()
#parser.add_argument("path_gen")
#parser.add_argument("path_result")
#parser.add_argument("nbr_ttl")
#parser.add_argument("model")

#args = parser.parse_args()

#path_gen=args.path_gen
#path_result=args.path_result
#nbr_ttl=args.nbr_ttl
#model=args.model

    ## SET constant ##

    # PATH constant where are stored the needed ressources, prompt, ontology and graph
    #path=Path(f'{os.getcwd()}/generate_ttl_files')
    #path_gen=Path(f'{path}/generate_ttl_files')
    #PATH=f'{os.getcwd()}/DIGITAL_TWIN/gengraphllm' # when using crontab
    path_ontology=f'{path_gen}/ontologies'
    path_prompt=f'{path_gen}/prompts'
    path_graph=f'{path_gen}/graph'

    ## PROMPT_TYPE to choose ##
    prompt_type='First_prompt'
    #PROMPT_TYPE='Second_prompt'
    #PROMPT_TYPE='Third_prompt'

    ## ONTOLOGY to choose ##
    onto='Noria'
    #ONTOLOGY='pygraph'

    ## choose MODEL ##
    #file_model = f'{path_gen}/model/models.txt'

    #model_list = []
    # Open the text file
    #with open(file_model, mode='r',encoding='utf-8') as file:
    #    lines = file.readlines()
    #    for line in lines:
    #        cleaned_line = line.strip()
    #        model_list.append(cleaned_line)

    #model = model_list[5]
    #date = datetime.datetime.now().strftime("%Y-%m-%d")

    #path_result = f'{path_gen.parent}/results/synthetics_graphs/{date}/{model}'
    bad_path_result = f'{path_result}/Bad_Turtle_Syntax'
    temp_file = f'{path_result}/temp.ttl'

    with open(f'{path_ontology}/Noria.ttl','rt',encoding='utf-8') as ontol:
        ontology = ','.join(str(x) for x in ontol.readlines())

    with open(f'{path_prompt}/{prompt_type}.txt','rt',encoding='utf-8') as prpt:
        prompt = ','.join(str(x) for x in prpt.readlines())

    # Only for second and third prompt
    #with open(f'{PATH_GRAPH}/full_graph.ttl','rt',encoding='utf-8') as graph:
    #    GRAPH = ','.join(str(x) for x in graph.readlines())

    os.makedirs(f'{path_result}', exist_ok=True)
    os.makedirs(f'{bad_path_result}', exist_ok=True)

    #arg = sys.argv[1:]
    #TARGET_NUMBER_OF_GRAPH = int(arg[0])
    number_of_graph = 0
    nbr_ttl_int = int(nbr_ttl)

    # remove the old files in path_result and bad_path_result
    if Path(path_result).exists() and Path(path_result).is_dir():
        for files in Path(path_result).iterdir():
            if files.is_file():
                files.unlink()

    if Path(bad_path_result).exists() and Path(bad_path_result).is_dir():
        for files in Path(bad_path_result).iterdir():
            if files.is_file():
                files.unlink()

    ## Generate graphs ##

    while number_of_graph != nbr_ttl_int:

        date_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_result = f'{path_result}/{prompt_type}_{date_time}_{onto}.ttl'
        bad_file_result = f'{bad_path_result}/{prompt_type}_{date_time}_{onto}_BAD.ttl'

        #Query LLM
        response=query_llm(prompt,ontology,model)

        #Store results
        storing_results(response,temp_file,file_result)

        # Check Turtle syntax
        check_ttl(file_result,bad_file_result,bad_path_result,0)

        print("Prompt tokens : ",response.usage.prompt_tokens)
        print("Output response tokens", response.usage.completion_tokens)

        number_of_graph += 1
        
    #check_identical_file()  TBD

    return f'{path_ontology}/Noria.ttl'
