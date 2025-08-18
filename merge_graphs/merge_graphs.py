'''This python script merge several knowledge Graphs in an only one. 
You have to pass as a parameter the folder where are stored the Graphs'''
import sys
import os
from pathlib import Path
from utils.utils_merge import rename_duplicates_nodes,remove_duplicate_prefix,find_duplicates_nodes
from utils.utils_merge import check_ttl

arg = sys.argv[1:]
PATH= arg[0]
nbr_dup= int(arg[1])

PATH_RESULT=f'{PATH}/merged_graph/'
MERGED_FILE=f'{PATH_RESULT}/merged_graph_{nbr_dup}.ttl'

BAD_PATH_RESULT=f'{PATH_RESULT}/Bad_Turtle_Syntax'
BAD_MERGED_FILE=f'{BAD_PATH_RESULT}/merged_graph_BAD.ttl'
OUTPUT_FILE_TEMP=f'{PATH_RESULT}/temp.ttl'

PATH_ONTOLOGY='../generate_graphs/ontologies/Noria.ttl'

#manage duplicate nodes in ttl files
duplicates=find_duplicates_nodes(PATH,PATH_ONTOLOGY)
rename_duplicates_nodes(PATH,duplicates,nbr_dup)

#Merge the ttl file
all_graphs = [f.name for f in Path(PATH).iterdir() if f.is_file()]
os.makedirs(f'{PATH_RESULT}',exist_ok=True)

# Open the output file in write mode
with open(OUTPUT_FILE_TEMP, 'w', encoding='utf-8') as outfile:
    for filename in all_graphs:
        # Open each input file in read mode
        with open(f'{PATH}/{filename}', 'r', encoding='utf-8') as infile:
            # Read the content and write it to the output file
            content = infile.read()
            outfile.write(content)
            outfile.write('\n')  # Adds a newline between files

# manage prefix in merged file
remove_duplicate_prefix(OUTPUT_FILE_TEMP,MERGED_FILE)

# validate ttl syntax
check_ttl(MERGED_FILE,BAD_MERGED_FILE,BAD_PATH_RESULT,1)
