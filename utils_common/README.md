# Utils Common

This folder contains common utility functions shared across the Ontology2Graph framework for argument parsing, logging setup, ontology processing, and file validation.

## Files Overview

### `utils.py`
Core utility module providing common functionality used throughout the Ontology2Graph framework.

**Main Features:**
- Command-line argument parsing and configuration
- File-based logger setup and management
- Ontology object extraction and processing
- TTL (Turtle) syntax validation and error handling

## Key Functions

### Argument Parsing
- **`setup_argument_parser(arguments)`**: Sets up command-line argument parsers with given descriptions and arguments
  - Supports special handling for mode arguments (basic/advanced choices)
  - Returns parsed arguments object
  - Used by all main scripts for consistent CLI interface

### Logging Management
- **`setup_logger(log_file, logger_name, level)`**: Creates and configures file-based loggers
  - Prevents duplicate FileHandlers for the same log file
  - Sets up formatted logging with timestamps and levels
  - Returns configured logger instance
  - Used throughout the framework for consistent logging

### Ontology Processing
- **`retreive_onto_object(ontology, object_type)`**: Extracts ontology objects from TTL files
  - Scans ontology files for specific object types (DatatypeProperty, ObjectProperty, Class)
  - Cleans object names by removing namespace prefixes
  - Returns list of cleaned object names
  - Supports ontology analysis and validation

### File Validation
- **`check_graph_syntax(file_path, bad_syntax_path, logger)`**: Validates TTL file syntax
  - Uses external Turtle validator to check file syntax
  - Automatically moves files with syntax errors to designated directory
  - Provides detailed logging of validation results
  - Reports statistics on checked and invalid files

## Integration

This utils_common module is used by:
- **generate_ttl_files**: TTL generation and validation
- **merge_ttl_files**: TTL merging operations and logging
- **display_graphs**: Graph visualization setup and logging

## Validation Support

The module includes comprehensive TTL syntax validation:
- **External validator integration**: Uses `ttl` command-line validator
- **Error isolation**: Moves invalid files to separate directory
- **Detailed logging**: Records all validation results and errors
- **Statistics reporting**: Provides counts of checked and invalid files

## Error Handling

- Graceful handling of missing files and directories
- Automatic creation of error directories when needed
- Comprehensive logging of all operations and errors
- Prevention of duplicate log handlers

## License

BSD-4-Clause License - Copyright (c) Orange SA

See the main LICENSE file for complete license terms.