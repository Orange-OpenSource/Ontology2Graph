
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
parser.add_argument("mode", help="Turtle validation or formatting")
args = parser.parse_args()

all_files = [f.name for f in Path(args.PATH).iterdir() if f.is_file()]

for i, file in enumerate(all_files):
    all_files[i]= args.PATH + file

# format each ttl file with owl-cli #
if args.mode=="format":
    for file_to_validate in all_files :
        command_format_ttl=["owl write --endOfLine lf --encoding utf_8 --indent space\
            --input TURTLE --output TURTLE", file_to_validate, file_to_validate]
        ttlvalidator=subprocess.Popen(command_format_ttl, stdout=subprocess.PIPE,\
            stderr=subprocess.PIPE,text=True)
        stdout, stderr = ttlvalidator.communicate()
        #print(file)
        #print(f'Turtle validator Result: {ttlvalidator.communicate()} \n')

        # check each ttl file with ttl validator #
elif args.mode=="validate":
    for file in all_files :
        command_validate_ttl=["ttl",file]
        ttlvalidator=subprocess.Popen(command_validate_ttl, stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        stdout, stderr = ttlvalidator.communicate()
        print(file)
        print(f'Turtle validator Result: {ttlvalidator.communicate()} \n')

elif args.mode!="validate" and args.mode!="format":
    print("Please use a correct mode argument value : validate or format")