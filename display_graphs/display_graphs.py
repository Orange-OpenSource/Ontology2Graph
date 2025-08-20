''' This python script compute some Knowledge Graphs KPIs and display the Graph.
You must pass as an argument the absolute path where are stored the ttl files or the PATH + the
file name for a single one file'''

import os
import sys
import subprocess
from pathlib import Path
from utils.utils_display import visu_graph,remove_literal_from_nodes,log_kpis,set_the_graph

arg = sys.argv[1:]
PATH= arg[0]
ONTOLOGY = os.path.expanduser('../generate_graphs/ontologies/noria_to_check.ttl')
CUMUL_NODES=0

if Path(PATH).is_file():
    print('this is a single file')
    FILE=[PATH]

    g, Graph, DiGraph, file_name = set_the_graph(PATH)
    remove_literal_from_nodes(g,Graph,DiGraph,ONTOLOGY)
    log_kpis(PATH,file_name,Graph,DiGraph,CUMUL_NODES)
    visu_graph(DiGraph,PATH)

    subprocess.run(['xterm', '-e', 'vim', f'{PATH}/html/Graphs.log'],check=True)

    sys.exit()

else :
    #List all the ttl graph files in PATH except folder
    all_files = [str(f.resolve()) for f in Path(PATH).iterdir() if f.is_file()]

    for file in all_files :

        g, Graph, DiGraph, file_name = set_the_graph(file)
        remove_literal_from_nodes(g,Graph,DiGraph,ONTOLOGY)
        CUMUL_NODES = log_kpis(PATH,file_name,Graph,DiGraph,CUMUL_NODES)
        visu_graph(DiGraph,file)

    subprocess.run(['xterm','-e','vim', f'{PATH}html/Graphs.log'],check=True)
