# Common Utilities Module

This folder contains common utility functions and scripts used throughout the Ontology2Graph framework for argument parsing, logging setup, ontology processing, file validation, and graph analysis operations.

## Python Files Overview

## Main Components:
- **utils_common/utils.py**: Core utility module providing foundational services used across all other modules in the framework.

    -  List of functions :
          - **setup_argument_parser**(arguments) : Sets up CLI argument parsers with special handling for mode arguments
          - **setup_logger**(log_file,logger_name,level) : Creates file-based loggers with formatted output
          - **retreive_onto_object**(ontology,object_type) : Extracts ontology objects from TTL files
          - **check_graph_syntax**(file_path,bad_syntax_path,logger) : Validates TTL syntax using external validator

## Features:
- Argument parsing and configuration management
- Logger setup and management
- Ontology object extraction and processing
- TTL (Turtle) syntax validation and error handling, require [Turtle Validator :fontawesome-solid-external-link-alt:](https://github.com/IDLabResearch/TurtleValidator){:target="_blank" rel="noopener"} tool accessible in system PATH
