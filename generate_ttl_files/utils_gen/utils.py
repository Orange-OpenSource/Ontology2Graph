"""
utils_gen.py provides utility functions for generating, validating, and storing knowledge graphs 
in Turtle (TTL) format using large language models (LLMs). It includes functions for querying
LLM APIs, storing and filtering results, validating TTL syntax, managing model selection,
and building file/folder paths and selecting prompt and ontology name. 

Main functionalities:
- Query LLMs to generate knowledge graphs based on prompts and ontologies
- Store and filter generated graph results
- Validate TTL files and handle errors
- Select LLM models from configuration
- Build and manage folder/file paths for graph operations
- Utility helpers for prompt and ontology selection
"""

import os
import json
from pathlib import Path
import datetime
from openai import OpenAI, OpenAIError

#from generate_ttl_files.generate_ttl import PROMPT_TYPE

def query_llm(ontology_file,prompt_file,model):
    """This function sends a prompt and an ontology schema to the LLM (via OpenAI-compatible API)
    and requests a graph generation using the specified model. The LLM is expected to return a 
    response containing the generated graph in Turtle format.

    Args:
        ontology (str): The ontology schema to guide the graph generation.
        model (str): The LLM model name to use for the API call.
        
    User Prompts to choose from:
        - "1_ip"  : (Initial prompt)
        - "2_ip_enhanced_manually' : (first enhancement by human)
        - "2_1_ip_enhanced_manually' : (second enhancement by human)
        - "3_ipem_enhanced_by_AI' : (prompt 2 enhanced by AI)
        - "3_1_ipem_enhanced_by_AI' : (prompt 2_1 enhanced by)
        - "4_prompt_fully_created_by_AI' : (fully created by AI)    
        - "4_1_AI_enhance_manually' : (fully created by AI and then manually enhanced)
        
    System Prompt to choose from:
        - "tokens_constraints" : (constraints on the number of tokens to use in the response)
        - "no_tokens_constraints" : (no constraints on the number of tokens to use in the response)

    Returns:
        openai.types.ChatCompletion | None: The response object from the LLM API if successful
        , otherwise None.
    """
    prompt_type="4_1_AI_enhance_manually"

    # Load prompts from a JSON file
    with open(prompt_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        prompt_system=data["prompt_system"]["tokens_constraints"]
        prompt_user=data["prompt_user"][prompt_type]

    with open(f'{ontology_file}','rt',encoding='utf-8') as ontol:
        ontology = ','.join(str(x) for x in ontol.readlines())

    client = OpenAI(api_key=os.environ.get("LLM_PROXY_KEY"),base_url="https://llmproxy.ai.orange")
    response= None
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.1,
            top_p=0.4,
            messages = [
                {   "role":"system",
                    "content":f"""{prompt_system}"""
                },
                {   "role": "user",
                    "content": f"""Follow the instruction : {prompt_user} and use the following
                    schema: {ontology} to generate a new graph in turtle format"""
                }
                       ]
            )

    except OpenAIError as e:
        print(f"An error occured: {e}")

    return response, prompt_type

def storing_results(response,temp_file,file_result,logger,model):
    """ Store the generated graph result from the LLM response, filter its content, and log 
    generation details. This function writes the LLM's response content to a temporary file,
    removes lines starting with '`', writes the filtered content to the final result file, logs
    information about the generation process (including model and token usage), and removes the
    temporary file.

    Args:
        response: The LLM API response object containing the generated graph and usage info.
        temp_file (str): Path to the temporary file for initial content storage.
        file_result (str): Path to the final output file for the filtered graph.
        logger: Logger object for recording generation details.
        model (str): The name of the LLM model used for generation."""

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

    logger.info('########### GRAPH GENERATION INFO ###########')

    if response is not None :
        if response.usage is not None:
            logger.info('FILE %s : has been generated', file_result)
            logger.info('Model used : %s',model)
            logger.info('Completion response tokens : %s',response.usage.completion_tokens)
            logger.info('Prompt tokens : %s',response.usage.prompt_tokens)
            logger.info('Total tokens : %s',response.usage.total_tokens)
            logger.info('Completion token details : %s\n',response.usage.completion_tokens_details)

    os.remove(temp_file)

def model_to_choose(model_nbr):
    """ Select a model name from the models.txt file based on the provided index.
    This function reads the list of available model names from the models.txt file and returns the
    model corresponding to the given index (model_nbr).

    Args:
        model_nbr (int): The index of the model to select from the list.
    Returns:
        str: The name of the selected model.
    """
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
    """Build and return paths for result folders, ontology, prompts, logs, and temporary files.
    This function constructs and creates (if necessary) the directory structure and file paths
    required for generating or merging knowledge graphs. It organizes output, logs, ontology,
    prompt files, and handles both generation and merging workflows.

    Args:
        model (str): The name of the model used for folder naming.
        gen_or_merge (str): Either 'gen' for generation or 'merge' for merging graphs.

    Returns:
        tuple: Paths for result folder, bad syntax folder, ontology file, prompt file, graph folder,
               temporary file, log file, and merged graph folder, in that order.
    """

    date = datetime.datetime.now().strftime("%Y-%m-%d")
    path_gen=Path(f'{os.getcwd()}')

    path_result = f'{path_gen.parent}/results/synthetics_graphs/{date}/{model}'
    ontologie_file=f'{path_gen}/ontologies/Noria.ttl'
    prompt_file=f'{path_gen}/prompts/prompts.json'
    path_graph=f'{path_gen}/graph'
    path_merged = f'{path_result}/merged'

    bad_path_result = f'{path_result}/Bad_Turtle_Syntax'
    temp_file = f'{path_result}/temp.ttl'
    date_other_format = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file=f'{Path(path_result)}/logs/generation_graph_{date_other_format}.log'

    os.makedirs(f'{path_result}/logs', exist_ok=True)
    os.makedirs(f'{path_merged}',exist_ok=True)
    os.makedirs(f'{bad_path_result}', exist_ok=True)

    ### remove previous log files in logs ###
    for filename in os.listdir(Path(log_file).parent):
        if filename.startswith('generation'):
            file_path = os.path.join(Path(log_file).parent, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

    return path_result, bad_path_result, ontologie_file, prompt_file, path_graph, temp_file,\
        Path(log_file),path_merged
