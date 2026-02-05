# Software Name : Ontologie2Graph
# SPDX-FileCopyrightText: Copyright (c) Orange SA
# SPDX-License-Identifier: BSD-4-Clause
#
# This software is distributed under the BSD 4-Clause "Original" or "Old" License,
# see the "LICENSE" file for more details or <license-url>

''' This script provides utility functions for generating, validating, and storing synthetics
knowledge graphs in Turtle (TTL) format. It includes functions for querying LLM APIs, storing and
filtering results, validating TTL syntax and ontological consistency, managing model selection,and
building file/folder paths and selecting prompt and ontology name. '''

import os
import shutil
import json
from pathlib import Path
import datetime
import subprocess
from openai import OpenAI, OpenAIError
import rdflib
from owlready2 import get_ontology,sync_reasoner_hermit,sync_reasoner_pellet
from owlready2 import OwlReadyInconsistentOntologyError,default_world

def query_llm(ontology_file,prompt_file,model,prompt_type):
    ''' This function sends a prompt and an ontology schema to an LLM (via OpenAI-compatible API)
    and requests a graph generation using the specified model. The LLM is expected to return a 
    response containing the generated graph in Turtle format.

    Args:
        ontology (str): The ontology schema to guide the graph generation.
        model (str): The LLM model name to use for the API call.

    System Prompt to choose from:
        - "tokens_constraints" : (constraints on the number of tokens to use in the response)
        - "no_tokens_constraints" : (no constraints on the number of tokens to use in the response)

    Returns:
        openai.types.ChatCompletion : The response object from the LLM API if successful, \
            otherwise None.'''

    ### Load prompts from a JSON file ###
    with open(prompt_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        prompt_user=data["prompt_user"][prompt_type]
        prompt_system=data["prompt_system"]["tokens_constraints"]

    ### Load ontology from a file ###
    with open(f'{ontology_file}','rt',encoding='utf-8') as ontol:
        ontology = ','.join(str(x) for x in ontol.readlines())

    client = OpenAI(api_key=os.environ.get("LLM_API_KEY"),base_url="YOUR API URL")
    response=None
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

    return response

def storing_results(response,temp_file,file_result,logger,model):
    ''' Store the generated graph result from the LLM response, filter its content, and log 
    generation details. This function writes the LLM's response content to a temporary file,
    removes lines starting with '`', writes the filtered content to the final result file, logs
    information about the generation process (including model and token usage), and removes the
    temporary file.

    Args:
        response: The LLM API response object containing the generated graph and usage info.
        temp_file (str): Path to the temporary file for initial content storage.
        file_result (str): Path to the final output file for the filtered graph.
        logger: Logger object for recording generation details.
        model (str): The name of the LLM model used for generation.'''

    with open(temp_file,'x',encoding='utf-8') as filetemp:
        filetemp.write(response.choices[0].message.content)
        filetemp.close()

    ### Remove lines started with '`' ###
    with open(temp_file,'r',encoding='utf-8') as file:
        lines = file.readlines()
        filtered_lines = [lines for lines in lines if not lines.startswith('`')]
        file.close()

    with open(file_result,'w',encoding='utf-8') as final:
        final.writelines(filtered_lines)
        final.close()

    if response is not None :
        if response.usage is not None:
            logger.info('FILE %s : has been generated', Path(file_result).name)
            logger.info('Model used : %s',model)
            logger.info('Completion response tokens : %s',response.usage.completion_tokens)
            logger.info('Prompt tokens : %s',response.usage.prompt_tokens)
            logger.info('Total tokens : %s',response.usage.total_tokens)
            logger.info('Completion token details : %s\n',response.usage.completion_tokens_details)

    os.remove(temp_file)

def model_to_choose(model_nbr):
    ''' Select a model name from the models.json file based on the provided index.
    This function reads the list of available model names from the models.json file and returns the
    model corresponding to the given index (model_nbr).

    Args:
        model_nbr (int) : The index of the model to select from the list.
    Returns:
        model_name : The name of the selected model.'''

    path_gen=Path(f'{os.getcwd()}')
    model_file = f'{path_gen}/utils_gen/models/models.json'

    ### Load model name from a JSON file ###
    with open(model_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        model_name=data["model"][str(model_nbr)]

    return model_name

def build_folder_paths_and_files(model):
    ''' Build and return paths for result folders, ontology, prompts, logs, and temporary files.
    This function constructs and creates (if necessary) the directory structure and file paths
    required for generating graphs. It organizes output, logs, ontology, prompt files, and handles 
    both generation and merging workflows.

    Args:
        model (str): The name of the model used for folder naming.

    Returns:
        tuple: Paths for result_folder, invalid syntax folder, misformatted turtle folder,
            invalid reasonner path,ontology file, prompt file, temporary file, log file, 
            and merged graph folder, in that order.'''

    date = datetime.datetime.now().strftime("%Y-%m-%d")
    path_gen=Path(f'{os.getcwd()}')

    ontologie_file=f'{path_gen}/utils_gen/ontologies/YOUR ONTOLOGIE FILE IN TURTLE FORMAT'
    prompt_file=f'{path_gen}/utils_gen/prompts/prompts.json'

    path_result = f'{path_gen.parent}/results/synthetics_graphs/{date}/{model}'

    if os.path.exists(path_result):
        shutil.rmtree(path_result)
    os.makedirs(Path(path_result))

    path_merged = f'{path_result}/merged'
    bad_syntax_path = f'{path_result}/Invalid_Turtle_Syntax'
    notformated_path = f'{path_result}/Notformatted_Turtle_file'
    invalid_reasoner_path = f'{path_result}/Invalid_Reasoner_Results'

    temp_file = f'{path_result}/temp.ttl'
    date_other_format = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file=f'{Path(path_result)}/logs/generation_graph_{date_other_format}.log'

    os.makedirs(f'{path_result}/logs', exist_ok=True)
    os.makedirs(f'{path_merged}',exist_ok=True)
    os.makedirs(f'{notformated_path}', exist_ok=True)
    os.makedirs(f'{bad_syntax_path}', exist_ok=True)
    os.makedirs(f'{invalid_reasoner_path}', exist_ok=True)

    ### remove previous log files in logs ###
    for filename in os.listdir(Path(log_file).parent):
        if filename.startswith('generation'):
            file_path = os.path.join(Path(log_file).parent, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

    return path_result, bad_syntax_path, notformated_path, invalid_reasoner_path, ontologie_file,\
        prompt_file, temp_file, Path(log_file), path_merged

def remove_file_in_folder(folder_path):
    ''' Remove all files in a specify folder

    Args:
        folder_path (str): The path to the folder from which files will be removed.'''

    if Path(folder_path).is_dir() and Path(folder_path).exists():
        for files in Path(folder_path).iterdir():
            if files.is_file():
                files.unlink()

def check_graph_format(folder_path, notformated_path, logger):
    '''Format TTL (Turtle) files using owl-cli tool.
    
    This function processes all TTL files in the specified folder, formatting them using the
    owl-cli command line tool with specific formatting options. Successfully formatted files
    replace the original files, while files that fail formatting are moved to a separate
    misformatted directory for manual inspection.
    
    The formatting process includes:
    - Setting line endings to LF (Linux format)
    - Using UTF-8 encoding
    - Applying space-based indentation
    - Converting from TURTLE input to TURTLE output format
    
    Args:
        folder_path (str): Path to the directory containing TTL files to be formatted.
        misformated_path (str): Path to the directory where misformatted files will be moved.
        logger_gen: Logger object for recording formatting operations and errors.
    
    Note:
        - Requires owl-cli to be installed and available in the system PATH
        - Files that cannot be formatted are renamed with "_MISFORMATED" suffix
        - The function uses a 30-second timeout for each formatting operation
        - Original files are replaced only when formatting is successful
    
    Raises:
        FileNotFoundError: When owl-cli command is not found in the system PATH.
        subprocess.TimeoutExpired: When formatting operation exceeds 30-second timeout.
        Exception: For other unexpected errors during the formatting process.'''

    all_files = [f.name for f in Path(folder_path).iterdir() if f.is_file()]

    print("\nChecking TTL file format : ...\n")
    logger.info('########### GRAPH FORMATING LOG ###########\n')
    ### format each ttl file with owl-cli ###
    for file in all_files :
        file_to_format= f"{folder_path}/{file}"
        formated_file_name = f"{folder_path}/{Path(file).stem}_FORMATED.ttl"

        logger.info('format file : %s',file)

        format_ttl_command = ["owl","write","--endOfLine","lf","--encoding", "utf_8",\
            "--indent", "space","--input", "TURTLE","--output", "TURTLE",file_to_format,
            formated_file_name]

        try:
            result = subprocess.run(format_ttl_command, capture_output=True, text=True, \
                timeout=30, check=False)

            if result.returncode == 0:
                os.replace(formated_file_name, file_to_format)
                logger.info(f"✓ Successfully formatted: {file}")
                print(f"{file} formatted successfully.")

            else:
                logger.error(f"✗ Error formatting {file}")
                logger.error(f"  Return code: {result.returncode}")
                logger.error(f"  Error output: {result.stderr}")
                logger.info(f"Moving {file} to notformated folder for manual check.")
                notformated_file_name = f"{Path(file).stem}_NOTFORMATED.ttl"
                os.replace(file_to_format, f"{notformated_path}/{notformated_file_name}")
                os.remove(formated_file_name)
                print(f"Error formatting {file}. Moved to notformated folder for manual check.")

        except subprocess.TimeoutExpired:
            logger.error(f"✗ Timeout formatting {file}")
            print(f"Timeout expired while formatting {file}")
        except FileNotFoundError:
            logger.error("✗ owl command not found. Make sure owl-cli is installed and in PATH")
            print("owl command not found. Make sure owl-cli is installed and in PATH")
        except (OSError, subprocess.SubprocessError) as e:
            logger.error(f"✗ Unexpected error formatting {file}: {e}")
            print(f"Unexpected error formatting {file}: {e}")

def check_graph_reasoner(folder_path, invalid_reasoner_path, ontology, reasoner, logger):
    ''' Validates knowledge graphs for ontological consistency using formal reasoning engines.

    This function performs comprehensive ontological consistency checking on TTL files by combining
    them with their corresponding ontology and applying formal logical reasoning engines
    (HermiT or Pellet). It identifies inconsistent ontology errors and unsatisfiable classes, 
    automatically quarantining invalid graphs.

    The validation process involves:
    1. Concatenating each graph with the ontology for complete context
    2. Converting to OWL/XML format for reasoning engine compatibility
    3. Applying the specified reasoner to detect logical inconsistencies
    4. Checking for unsatisfiable classes (equivalent to owl:Nothing)
    5. Moving invalid graphs to a quarantine directory with INVALID_ prefix

    Args:
        folder_path (str): Path to directory containing TTL graph files to validate
        invalid_reasoner_path (str): Path to directory for quarantining invalid graphs
        ontology (str): Path to the ontology TTL file used for consistency checking
        reasoner (str): Reasoning engine to use ("HermiT" or "Pellet")
        logger: Logging instance for recording validation results and errors

    Returns:
        None: Function performs validation and file management operations

    Raises:
        OwlReadyInconsistentOntologyError: When reasoner detects ontological inconsistencies
        OverflowError: When system resource limits are exceeded during reasoning

    Side Effects:
        - Creates temporary OWL/XML files during processing (automatically cleaned up)
        - Moves invalid graphs to quarantine directory
        - Logs detailed validation results and error information
        - Prints progress and results to console'''

    all_graph_to_check = [f for f in Path(folder_path).iterdir() if f.is_file()]

    print("\nChecking TTL files reasoning consistency ...\n")
    logger.info('########### CHECK GRAPH REASONER LOG ###########\n')

    ### Check each graph ###
    for graph_to_check in all_graph_to_check :
        print(f'\nchecking graph: {graph_to_check.name}')
        logger.info('Checking graph %s with reasoner %s\n', graph_to_check.name, reasoner )

        ### Concat ontology and graph in the same file ###
        with open(ontology, 'r', encoding='utf-8') as f1,\
             open(graph_to_check, 'r', encoding='utf-8') as f2:
            content1 = f1.read()
            content2 = f2.read()

        concatenated_file = content1 + content2

        ### Load concatenated graph with RDFLib ###
        skgraph = rdflib.Graph()
        skgraph.parse(data=concatenated_file, format="turtle")

        ### Convert RDFLib graph to OWL/XML format ###
        graph_xml = skgraph.serialize(format="xml")
        encoded_graph = graph_xml.encode('utf-8')

        ### Save the OWL/XML graph to a temporary graph ###
        with open(f'temp_graph_{Path(graph_to_check).name}', "wb") as temp_graph:
            temp_graph.write(encoded_graph)

        encoded_graph_to_check=get_ontology(f'file://temp_graph_{Path(graph_to_check).name}').load()

        try:
            with encoded_graph_to_check:
                if reasoner=="HermiT":
                    sync_reasoner_hermit(debug=0, keep_tmp_file=True,
                                      ignore_unsupported_datatypes = True)
                if reasoner=="Pellet":
                    sync_reasoner_pellet(debug=0, keep_tmp_file=True)

        except OwlReadyInconsistentOntologyError as onto_e:
            print(f'OwlReadyInconsistentOntologyError detected by {reasoner} for '
                  f'{Path(graph_to_check).name}')
            logger.info('OwlReadyInconsistentOntologyError detected by %s \n',reasoner)
            logger.info(onto_e)
            os.rename(graph_to_check,f"{invalid_reasoner_path}/INVALID_{Path(graph_to_check).name}")
            logger.info(f'File {Path(graph_to_check).name} moved to {invalid_reasoner_path}\n')

        except OverflowError as e: #system ressource limits reach
            print(f"\nOverFlowError : {e}")
            logger.info('OverFlowError : ',e)
            os.rename(graph_to_check,f"{invalid_reasoner_path}/INVALID_{Path(graph_to_check).name}")
            logger.info(f'File {Path(graph_to_check).name} moved to {invalid_reasoner_path}\n')

        else :
            print(f'\nNo inconsistent Ontology errors detected by {reasoner} for '
                  f'{Path(graph_to_check).name}')
            logger.info('No inconsistent Ontology errors found by %s ',reasoner)

        ### List classes inferred equivalent to owl:Nothing (unsatisfiable classes) ###
        unsat = list(default_world.inconsistent_classes())
        if unsat:
            print(f'inconsistent classes found by {reasoner} :\n')
            for c in unsat:
                print(" - \n", c)
                logger.info('inconsistent classes found by %s',reasoner)
                logger.info(' %s',c)
                os.rename(graph_to_check, f"{invalid_reasoner_path}"\
                          f"INVALID_{Path(graph_to_check).name}")
                logger.info(f'File {Path(graph_to_check).name} moved to {invalid_reasoner_path}\n')
        else:
            print(f'No inconsistent classes found by {reasoner} for'
                  f'{Path(graph_to_check).name}')
            logger.info('No inconsistent classes found by %s \n',reasoner)

        if Path(f'{Path(f'{os.getcwd()}')}/temp_graph_{Path(graph_to_check).name}').is_file():
            os.remove(Path(f'{Path(f'{os.getcwd()}')}/temp_graph_{Path(graph_to_check).name}'))
