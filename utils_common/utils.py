''' this script contains common function used by several python files '''

import argparse
import datetime
import os
import logging
from pathlib import Path

def setup_argument_parser(parser, arguments):
    """ Sets up an argument parser with the given description and arguments.
    Args:
        parser (argparse.ArgumentParser): The argument parser to set up.
        arguments (list of tuples): Each tuple contains (name, help) for an argument.
    """
    parser = argparse.ArgumentParser()
    for name, help_text in arguments:
        parser.add_argument(name, help=help_text)

    args = parser.parse_args()
    return args

def remove_file_in_folder(folder_path):
    '''remove all files in a folder'''
    if Path(folder_path).is_dir() and Path(folder_path).exists():
        for files in Path(folder_path).iterdir():
            if files.is_file():
                files.unlink()

def setup_logger(log_file,logger_name):
    '''setup logger configuration'''
    logger = logging.getLogger(logger_name)
    handler = logging.FileHandler(Path(log_file))
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger

def build_folder_paths_and_files(model,gen_or_merge):
    '''build folder paths and files'''

    if gen_or_merge not in ['gen','merge']:
        raise ValueError("gen_or_merge must be either 'gen' or 'merge'")

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
    log_file=f'{Path(path_result)}/no_log_file.log'
    if gen_or_merge=='gen':
        log_file=f'{Path(path_result)}/nodes_log/generate_{date_other_format}.log'
    elif gen_or_merge=='merge':
        log_file=f'{Path(path_result)}/merged/merge_{date_other_format}.log'

    os.makedirs(f'{path_result}/nodes_log', exist_ok=True)
    os.makedirs(f'{path_merged}',exist_ok=True)
    os.makedirs(f'{bad_path_result}', exist_ok=True)

    return path_result, bad_path_result, path_ontologies, path_prompt, path_graph, temp_file,\
        log_file,path_merged
