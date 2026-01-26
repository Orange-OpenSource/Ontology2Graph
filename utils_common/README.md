# Utils Folder

This folder contains utility scripts for processing and validating Turtle (.ttl) files and extracting graph data. Each script is designed to perform a specific task related to knowledge graph management.

## Contents

- `extract_nodes_from_files.py`: Extracts node names from a Turtle file and saves them to a CSV file. Useful for analyzing graph structure and node lists.
- `find_duplicates_nodes.py`: Scans all Turtle files in a directory to find duplicate nodes. Helps identify redundancy or errors in graph data.
- `validate_ttl.py`: Validates all Turtle files in a specified directory using the `ttl` command-line validator. Prints validation results for each file.
- `script_crontab.sh`: (If present) Shell script for scheduling or automating tasks related to the utils.

## Usage

### Extract Nodes
```bash
python extract_nodes_from_files.py <file.ttl>
```
- Outputs a CSV file listing all nodes found in the Turtle file.

### Find Duplicate Nodes
```bash
python find_duplicates_nodes.py <directory_path>
```
- Scans all `.ttl` files in the directory and reports duplicate nodes.

### Validate Turtle Files
```bash
python validate_ttl.py <directory_path>
```
- Runs the `ttl` validator on each `.ttl` file in the directory and prints results.

## Requirements
- Python 3.x
- `rdflib`, `networkx` (for graph processing)
- `ttl` command-line tool (for validation)

## Notes
- Ensure all dependencies are installed in your Python environment.
- Scripts expect absolute or relative paths as arguments.

## License
BSD-4-Clause License - Copyright (c) Orange SA

See the main LICENSE file for complete license terms.