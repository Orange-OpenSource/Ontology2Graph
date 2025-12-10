''' function used to generate graphs from llm '''

import os
import shutil
from pathlib import Path
import subprocess
import datetime
from openai import OpenAI, OpenAIError

def query_llm(prompt,ontology,model):
    '''quey llm API'''

    #client = genai.Client()
    client = OpenAI(api_key=os.environ.get("LLM_PROXY_KEY"),base_url="https://llmproxy.ai.orange")
    response= None
    try:
        response = client.chat.completions.create(
        #response = client.completions.create(
            model=model,
            temperature=0.1, # model's creativity
            top_p=0.4, # model's creativity
            #reasoning_effort=reas_eff,
            #extra_body={
            #        'extra_body': {
            #            "google": {
            #                "thinking_config": {
            #                    "thinking_budget": -1,
            #                    "include_thoughts":True
            #                }
            #            }
            #        }
            #},
            #input=prompt)
            #max_tokens=max_tok, # sum of reasoning tokens and text tokens
            #max_completion_tokens=max_tok,
            #frequency_penalty=1, #Applies a penalty to repeated tokens, reducing the likelihood
            # of repetition in the generated text.
            #presence_penalty=1, # Applies a penalty to tokens that have already appeared in the
            # generated text, further reducing repetition.
            #reasoning_effort="high",
            messages = [
                {   "role":"system",
                    "content":"""You are an expert in websemantic technologies and most 
                    particulary in knowledge graph and ttl format. 
                    Please provide detailed and comprehensive responses to the following queries. 
                    Ensure that your answers are as thorough as possible.
                    """
                },
                {   "role": "user",
                    "content": f"""Follow the instruction : {prompt} and use the following schema:
                    {ontology} to generate a new graph in turtle format"""
                }
                       ]
            )

    except OpenAIError as e:
        print(f"An error occured: {e}")

    if response is not None:
        return response

def storing_results(response,temp_file,file_result):
    '''store and clean results'''

    with open(temp_file,'x',encoding='utf-8') as filetemp:
        filetemp.write(response.choices[0].message.content)
        filetemp.close()

    #Remove lines started with '
    with open(temp_file,'r',encoding='utf-8') as file:
        lines = file.readlines()
        filtered_lines = [lines for lines in lines if not lines.startswith('`')]
        file.close()

    with open(file_result,'w',encoding='utf-8') as final:
        final.writelines(filtered_lines)
        final.close()

    os.remove(temp_file)

def check_ttl(file_result, bad_file_result, bad_path_result,merged):
    '''check ttl syntax store wrong file in specific folder and 
    maek a copy of right ttl file'''
    command=["ttl",file_result]
    ttlvalidator = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    stdout, stderr = ttlvalidator.communicate()

    if stdout!='Validator finished with 0 warnings and 0 errors.\n' :
    # move bad file in bad folder and Save logs
        print(f'\nFILE {Path(file_result).name} has been generated with errors')
        os.makedirs(f'{bad_path_result}', exist_ok=True)
        shutil.move(file_result, bad_file_result)
    else:    # make a copy of right files
        print(f'\nFILE {Path(file_result).name} has been generated succesffully without errors')

    if merged==1:
        print(f'Merged graph : Turtle validator Result: {stdout}'.rstrip('\n'))
    else:
        print(f'Turtle validator Result: {stdout}'.rstrip('\n'))

    return stdout

def ttl_validator(path):
    '''validate ttl merged graph'''
    all_files = [f.name for f in Path(path).iterdir() if f.is_file()]

    for i, file in enumerate(all_files):
        all_files[i]= path + file

    for file in all_files :
        command=["ttl",file]
        ttlvalidator=subprocess.Popen(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                      text=True)
        stdout, stderr = ttlvalidator.communicate()
        print(file)
        print(f'Merged graph : Turtle validator Result: {stdout},{stderr}')
        print('\n')

def model_to_choose(model_nbr):
    '''choose model from model.txt file model_nbr : int value to choose the model in file_list'''
    path_gen=Path(f'{os.getcwd()}')
    model_list = []
    file_list = f'{path_gen}/model/models.txt'
    with open(file_list, mode='r',encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            cleaned_line = line.strip()
            model_list.append(cleaned_line)
    model = model_list[model_nbr]
    return model

def build_folder_paths_and_files(model):
    '''build folder paths and files'''

    date = datetime.datetime.now().strftime("%Y-%m-%d")
    path_gen=Path(f'{os.getcwd()}')

    path_result = f'{path_gen.parent}/results/synthetics_graphs/{date}/{model}'
    path_ontologies=f'{path_gen}/ontologies'
    path_prompt=f'{path_gen}/prompts'
    path_graph=f'{path_gen}/graph'
    path_merged = f'{path_result}/merged_graph'

    bad_path_result = f'{path_result}/Bad_Turtle_Syntax'
    temp_file = f'{path_result}/temp.ttl'
    date_other_format = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file=f'{Path(path_result)}/nodes_log/generate_{date_other_format}.log'

    os.makedirs(f'{path_result}/nodes_log', exist_ok=True)
    os.makedirs(f'{bad_path_result}', exist_ok=True)

    return path_result, bad_path_result, path_ontologies, path_prompt, path_graph, temp_file,\
        log_file,path_merged

def remove_file_in_folder(folder_path):
    '''remove all files in a folder'''
    if Path(folder_path).is_dir() and Path(folder_path).exists():
        for files in Path(folder_path).iterdir():
            if files.is_file():
                files.unlink()

def prompt_type_and_ontology_name():
    '''choose prompt type and ontology'''

    #prompt_type='1_initial_prompt_ip'
    #prompt_type='2_ip_enhanced_manually_ipem'
    #prompt_type='2_1_ip_enhanced_manually_ipem'
    #prompt_type='3_ipem_enhanced_by_AI'
    #prompt_type='3_1_ip_enhanced_manually_ipem_enhanced_by_AI'
    #prompt_type='4_prompt_fully_created_by_AI'
    prompt_type='4_1_prompt_fully_created_by_AI'
    #prompt_type='4_2_created_by_gemini' #generated with gemini

    onto_name = 'Noria'

    return prompt_type, onto_name

def log(file_result, bad_file_result, ttl_validator_output,response,model,logger_gen):
    '''log generation info'''

    logger_gen.info('########### GRAPH GENERATION INFO ###########')

    if ttl_validator_output=='Validator finished with 0 warnings and 0 errors.\n' :
        logger_gen.info('\nFILE : %s has been generated succesffully without errors',
                    Path(file_result).name)
        logger_gen.info('Result : %s', ttl_validator_output)
    else:
        logger_gen.info('\nFILE %s : has been generated with errors', Path(bad_file_result).name)
        logger_gen.info('Result: %s', ttl_validator_output)

    if response is not None :
        if response.usage is not None:
            logger_gen.info('Model used : %s',model)
            logger_gen.info('Completion response tokens : %s',response.usage.completion_tokens)
            logger_gen.info('Prompt tokens : %s',response.usage.prompt_tokens)
            logger_gen.info('Total tokens : %s',response.usage.total_tokens)
            logger_gen.info('Completion token details : %s',\
                response.usage.completion_tokens_details)
