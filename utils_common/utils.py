
""" Common utility functions for gengraphllm
Provides shared utility functions used across multiple scripts in the project,including:
- Argument parser setup
- File removal utilities
- Logger configuration
"""
import argparse
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

def get_last_folder_part(string, sep_char):
    """get last part of a folder string"""
    string_parts=string.split(sep_char)
    last_part=string_parts[len(string_parts)-1]
    if last_part=='':
        last_part=string_parts[len(string_parts)-2]
    return last_part

def retreive_datatype_properties(ontology):
    '''create a list of all the data type properties from the ontologie'''

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
    '''create a list of all the data type properties from the ontologie'''

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
    return objproperties
