'''ttlvalidator'''
import sys
from pathlib import Path
import subprocess

arg = sys.argv[1:]
PATH= arg[0]

all_files = [f.name for f in Path(PATH).iterdir() if f.is_file()]

for i, file in enumerate(all_files):
    all_files[i]= PATH + file

for file in all_files :
    command=["ttl",file]
    ttlvalidator=subprocess.Popen(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    stdout, stderr = ttlvalidator.communicate()
    print(file)
    print(f'Turtle validator Result: {ttlvalidator.communicate()}')
    print('\n')
