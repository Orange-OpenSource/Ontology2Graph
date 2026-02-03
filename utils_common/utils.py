# Software Name : Ontologie2Graph
#
# SPDX-FileCopyrightText: Copyright (c) Orange SA
# SPDX-License-Identifier: BSD-4-Clause
#
# This software is distributed under the BSD 4-Clause "Original" or "Old" License,
# see the "LICENSE" file for more details or <license-url>

''' utils_common/utils.py

This module provides common utility functions for argument parsing, logging setup, ontology object\
retrieval, and TTL syntax validation. It is used throughout the GenGraphLLM framework to support\
script configuration, logging, and basic ontology file operations.

Main functionalities:
- Argument parser setup for command-line scripts
- Logger configuration for file-based logging
- Ontology object extraction (classes, properties)
- Syntax checking for Turtle files '''

import argparse
import logging
import os
import subprocess
import shutil
from pathlib import Path

def setup_argument_parser(arguments):
    ''' Sets up an argument parser with the given description and arguments.
    Args:
        parser (argparse.ArgumentParser): The argument parser to set up.
        arguments (list of tuples): Each tuple contains (name, help) for an argument.'''

    parser = argparse.ArgumentParser()

    for name, help_text in arguments:
        if name=="mode": # special case for mode argument in display_graphs.py
            parser.add_argument(name, help=help_text, choices=['basic','advanced'])
        else:
            parser.add_argument(name, help=help_text)

    args = parser.parse_args()
    return args

def setup_logger(log_file,logger_name,level):

    '''Set up and configure a logger for file-based logging.

    This function creates or retrieves a logger with the specified name and logging level, and \
    attaches a FileHandler to write logs to the given log_file. The log format includes timestamp,\
    log level, and message. If a FileHandler for the log_file exists, it will not add another.

        Args:
            log_file (str or Path): Path to the log file where logs will be written.
            logger_name (str): Name of the logger instance.
            level (int): Logging level (e.g., logging.INFO, logging.DEBUG).

        Returns:
            logging.Logger: Configured logger instance.'''

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == str(Path(log_file))
        for h in logger.handlers):
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

def retreive_onto_object(ontology,object_type):

    '''Extracts and returns a list of ontology objects of a specified type from a Turtle (.ttl)\
    ontology file.

    This function scans the ontology file for lines declaring objects of the given type \
    (e.g., DatatypeProperty, ObjectProperty, or Class), cleans the object names, and returns\
    them as a list of strings.

    Args:
        ontology (str or Path): Path to the ontology Turtle file to parse.
        object_type (str): The type of ontology object to extract (e.g., "DatatypeProperty",\
        "ObjectProperty", "Class").

    Returns:
        list: A list of cleaned object names declared in the ontology of the specified type.'''

    index_list=[]
    objects=[]
    object_clean=[]

    ### build index list of Object ###
    with open(f'{ontology}', 'r',encoding='utf-8') as file:
        for index, line in enumerate(file, start=1):
            if f":{object_type} " in line :
                index_list.append(index-1)
    file.close()

    ### retrieve Object based on index list ###
    with open(f'{ontology}', 'r',encoding='utf-8') as file:
        for index, line in enumerate(file, start=1):
            if index in index_list:
                objects.append(line.strip())

    file.close()

    ### clean Object ###
    for obj in objects:
        obj=obj.replace('noria:',"")
        object_clean.append(obj)

    return object_clean

def check_graph_syntax(file_path,bad_syntax_path,logger):
    '''Checks the syntax of all TTL files in a directory using an external Turtle validator.
    Moves files with syntax errors to a specified directory and logs the results.

    Args:
        file_path (str): Path to the directory containing TTL files to check.
        bad_file_path (str): Path to the directory where invalid TTL files will be moved.
        logger (logging.Logger): Logger object for recording validation results and errors.

    Behavior:
        - Iterates over all files in file_path.
        - Runs a Turtle syntax validator on each file.
        - If a file has errors, moves it to bad_file_path and log errors.
        - Prints and logs the number of files checked and the number of bad files found.'''

    nbr_file = 0
    count = 0
    bad_file_number = 0
    file_list = [f.name for f in Path(file_path).iterdir() if f.is_file()]

    logger.info('######## TURTLE SYNTAX CHECK LOG ########\n')

    with os.scandir(file_path) as entries:
        for entry in entries:
            if entry.is_file():
                nbr_file += 1

    print("\nChecking TTL files syntax ...")
    print('\nNumber of file to check : ',nbr_file)

    while count != nbr_file:

        file=f'{file_path}/{file_list[count]}'
        file_name=Path(file).name

        command=["ttl",file]
        ttlvalidator=subprocess.Popen(command, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,text=True)
        stdout, stderr = ttlvalidator.communicate()
        logger.info('Graph : %s',file_name)

        if stdout!='Validator finished with 0 warnings and 0 errors.\n' :
        ### move bad file in bad folder and Save logs ###
            bad_file=f'{bad_syntax_path}/BAD_{file_name}'
            os.makedirs(f'{bad_syntax_path}', exist_ok=True)
            shutil.move(file, bad_file)
            logger.info('Error detected in : %s', file_name)
            logger.info('Turtle validator Result: %s %s',stdout, stderr)
            logger.info(f'file {file_name} moved to {bad_syntax_path}\n')
            bad_file_number += 1
        else:
            logger.info('No error detected in : %s\n', file_name)

        count += 1

    if bad_file_number != 0:
        print(f'Number of bad files detected : {bad_file_number}')
        print(f'Bad files moved to : {bad_syntax_path}\n')
    else:
        print('No bad file detected\n')

#### old code below for reference ####

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
            with the 'noria:' prefix removed.

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
    return dtproperties'''

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
