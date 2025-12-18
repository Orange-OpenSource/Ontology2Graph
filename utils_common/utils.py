
""" Common utility functions for gengraphllm
Provides shared utility functions used across multiple scripts in the project,including:
- Argument parser setup
- File removal utilities
- Logger configuration
"""
import argparse
import logging
import os
import subprocess
import shutil
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
    logger.setLevel(logging.INFO)
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == str(Path(log_file))\
        for h in logger.handlers):
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

def get_last_folder_part(string, sep_char):
    """get last part of a folder string
    string_parts=string.split(sep_char)
    last_part=string_parts[len(string_parts)-1]
    if last_part=='':
        last_part=string_parts[len(string_parts)-2]
    return last_part"""

def retreive_datatype_properties(ontology):
    '''Extracts all datatype properties from an ontology file.
    Args:
        ontology (str): Path to the ontology file (TTL format) to be processed.
    Returns:
        list: A list of datatype property names (as strings) found in the ontology, \
            with the 'noria:' prefix removed.'''

    index_list=[]
    dtprop=[]
    dtproperties=[]

    #build index list of DatatypeProperty
    with open(f'{ontology}', 'r',encoding='utf-8') as file:
        for index, line in enumerate(file, start=1):
            if 'DatatypeProperty' in line :
                index_list.append(index-1)
    file.close()

    #retreive DatatypeProperties based on index list
    with open(f'{ontology}', 'r',encoding='utf-8') as file:
        for index, line in enumerate(file, start=1):
            if index in index_list:
                dtprop.append(line.strip())
                #print(line.strip())
    file.close()

    #clean DatatypeProperties
    for dtp in dtprop:
        dtp=dtp.replace('noria:',"")
        dtproperties.append(dtp)
    return dtproperties

def retreive_object_properties(ontology):
    """create a list of all the data type properties from the ontologie

    index_list=[]
    objprop=[]
    objproperties=[]

    #build index list of ObjectProperty
    with open(f'{ontology}', 'r',encoding='utf-8') as file:
        for index, line in enumerate(file, start=1):
            if 'ObjectProperty' in line :
                index_list.append(index-1)
    file.close()

    #retreive ObjectProperties based on index list
    with open(f'{ontology}', 'r',encoding='utf-8') as file:
        for index, line in enumerate(file, start=1):
            if index in index_list:
                objprop.append(line.strip())
                #print(line.strip())
    file.close()

    #clean ObjectProperties
    for objp in objprop:
        objp=objp.replace('noria:',"")
        objproperties.append(objp)
    return objproperties"""

def check_ttl(file_path,bad_file_path,logger):
    """Checks the syntax of all TTL files in a directory using an external Turtle validator.
    Moves files with syntax errors to a specified directory and logs the results.

    Args:
        file_path (str): Path to the directory containing TTL files to check.
        bad_file_path (str): Path to the directory where invalid TTL files will be moved.
        logger (logging.Logger): Logger object for recording validation results and errors.

    Behavior:
        - Iterates over all files in file_path.
        - Runs a Turtle syntax validator on each file.
        - If a file has errors, moves it to bad_file_path and log errors.
        - Prints and logs the number of files checked and the number of bad files found."""

    nbr_file = 0
    count = 0
    bad_file_number = 0
    file_list = [f.name for f in Path(file_path).iterdir() if f.is_file()]
    logger.info('######## Turtle concistency check ########\n')

    with os.scandir(file_path) as entries:
        for entry in entries:
            if entry.is_file():
                nbr_file += 1

    print("\nChecking TTL files syntax ...")
    print('\nNumber of file to check : %s',nbr_file)

    while count != nbr_file:

        file=f'{file_path}/{file_list[count]}'
        file_name=Path(file).name

        command=["ttl",file]
        ttlvalidator=subprocess.Popen(command, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,text=True)
        stdout, stderr = ttlvalidator.communicate()
        logger.info('Graph : %s',file_name)

        if stdout!='Validator finished with 0 warnings and 0 errors.\n' :
        # move bad file in bad folder and Save logs
            bad_file=f'{bad_file_path}/{file_name}_BAD.ttl'
            os.makedirs(f'{bad_file_path}', exist_ok=True)
            shutil.move(file, bad_file)
            logger.info('Error detected in : %s', file_name)
            logger.info('Turtle validator Result: %s',stdout)
            bad_file_number += 1
        else:
            logger.info('No error detected in : %s\n', file_name)

        count += 1

    if bad_file_number != 0:
        print(f'Number of bad files detected : {bad_file_number}')
