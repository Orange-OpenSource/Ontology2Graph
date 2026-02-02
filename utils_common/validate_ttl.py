
#!/usr/bin/env python3
# Software Name : Ontologie2Graph
# SPDX-FileCopyrightText: Copyright (c) Orange SA
# SPDX-License-Identifier: BSD-4-Clause
#
# This software is distributed under the BSD 4-Clause "Original" or "Old" License,
# see the "LICENSE" file for more details or <license-url>

'''TTL File Syntax Validator

This script validates the syntax of Turtle (TTL) RDF files in a specified directory using an 
external TTL validator tool. It processes all TTL files in the given path andd reports validation
results for each file.

The script performs the following operations:
1. Scans the specified directory for all files
2. Runs the TTL validator tool on each file
3. Captures and reports validation results (stdout/stderr)
4. Provides feedback on syntax correctness for each file

This tool is useful for:
- Quality assurance of generated TTL files
- Batch validation of knowledge graph collections
- Identifying syntax errors before graph processing
- Ensuring RDF compliance in automated workflows

Usage:
    python validate_ttl.py <path_to_ttl_directory>

Arguments:
    PATH: Path to the directory containing TTL files to validate

Output:
    For each file processed, prints:
    - File path being validated
    - TTL validator results (success/error messages)

Requirements:
    - External 'ttl' command-line validator tool must be installed and available in PATH
    - The validator tool should accept a file path as argument and return validation status

Dependencies:
    - argparse: For command-line argument parsing
    - pathlib: For cross-platform path handling
    - subprocess: For executing external TTL validator command

Example:
    python validate_ttl.py /path/to/ttl/files/
    # Output:
    # /path/to/ttl/files/graph1.ttl
    # Turtle validator Result: (None, None)
    # 
    # /path/to/ttl/files/graph2.ttl
    # Turtle validator Result: (None, 'Error: Invalid syntax at line 10') '''

import argparse
from pathlib import Path
import subprocess

### set argument parser ####
parser = argparse.ArgumentParser()
parser.add_argument("PATH", help="Path where the files to validate are stored")
args = parser.parse_args()

all_files = [f.name for f in Path(args.PATH).iterdir() if f.is_file()]

for i, file in enumerate(all_files):
    all_files[i]= args.PATH + file

for file in all_files :
    command_validate_ttl=["ttl",file]
    ttlvalidator=subprocess.Popen(command_validate_ttl, stdout=subprocess.PIPE,\
        stderr=subprocess.PIPE,text=True)
    print(file)
    print(f'Turtle validator Result: {ttlvalidator.communicate()} \n')
