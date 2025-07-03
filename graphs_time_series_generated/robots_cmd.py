'''This python scipt launch robots commands on a list of ttl files stored in a folder. You must
pass as an argument the location folder where are stored all the ttl files'''

import sys
import os
import glob
import subprocess

arg = sys.argv[1:]
PATH= arg[0]
PATH_ROBOT=f'{PATH}/robot_measurements'
ROBOT_CMD='measure'
#ROBOT_CMD='reasoner'
#ROBOT_CMD='report'
#ROBOT_CMD='export'

os.makedirs(f'{PATH_ROBOT}/',exist_ok=True)

def replace_char_at_index(original_string, index_to_replace, new_character):
    '''replacement of characters that doesn't conform to the date format'''
    return original_string[:index_to_replace] + new_character + original_string[index_to_replace+1:]

#List all the files
all_files = glob.glob(os.path.join(PATH, '*'))

for file in all_files:

    #retreive file name without folder
    parts = file.split("/")
    file_name_pos = len(parts)
    file_name = parts[file_name_pos-1]

    #Build file name for robots results
    file_robot = file_name[:len(file_name)-4] + f'_robot_{ROBOT_CMD}.csv'

    command=["robot","measure","--input",f'{file}',"--metrics","all","--format","csv","--output",
             f'{PATH_ROBOT}/{file_robot}']

    robot_gen=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)

    stdout, stderr = robot_gen.communicate()

    if stderr == '' :
        print(f'robot generator Result: {file_robot} generated')
