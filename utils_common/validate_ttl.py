
""" This script validates all Turtle (.ttl) files stored in a directory using the 'ttl'
command-line validator.
Usage:
    python validate_ttl.py <PATH>
Arguments:
    PATH: Path to the directory containing Turtle files to validate.
For each file, the script runs the validator and prints the file name and validation output.
"""

import argparse
from pathlib import Path
import subprocess

# set argument parser #
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
    stdout, stderr = ttlvalidator.communicate()
    print(file)
    print(f'Turtle validator Result: {ttlvalidator.communicate()} \n')
