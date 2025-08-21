''' This python script compute some Knowledge Graphs KPIs and display the Graph.
You must pass as an argument the absolute path where are stored the ttl files or the PATH + the
file name for a single one file'''

import os
import sys
import subprocess
import logging
from pathlib import Path
from utils.utils_display import visu_graph,remove_literal_from_nodes,log_kpis,set_the_graph

arg = sys.argv[1:]
PATH= arg[0]
ONTOLOGY = os.path.expanduser('../generate_graphs/ontologies/noria_to_check.ttl')
CUMUL_NODES=0

if Path(PATH).is_file():
    print('this is a single file')
    absolute_folder=Path(PATH).parent.resolve()
    file_name=Path(PATH).name
    ABSOLUTE_FILE_NAME=f'{absolute_folder}/{file_name}'

    g, Graph, DiGraph, file_name = set_the_graph(PATH)

    #print(DiGraph.nodes)
    remove_literal_from_nodes(g,Graph,DiGraph,ONTOLOGY)


    logging.basicConfig(level=logging.INFO, filename=f'{absolute_folder}/html/Digraph.log',
                        filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

    for s, p, data in DiGraph.edges(data=True):
        print((s,p,data))
        #logging.info(f'{(s,p,data)}')

    #print(DiGraph)
    log_kpis(Path(PATH),file_name,Graph,DiGraph,CUMUL_NODES)

    #print(DiGraph.nodes)
    #print(len(DiGraph.nodes))
    visu_graph(DiGraph,ABSOLUTE_FILE_NAME)
    #subprocess.run(['xterm', '-e', 'vim', f'{PATH}/html/Graphs.log'],check=True)
    sys.exit()

else :
    #List all the ttl graph files in PATH except folder
    all_files = [str(f.resolve()) for f in Path(PATH).iterdir() if f.is_file()]

    for file in all_files :

        g, Graph, DiGraph, file_name = set_the_graph(file)
        print(DiGraph)
        remove_literal_from_nodes(g,Graph,DiGraph,ONTOLOGY)
        print(DiGraph)
        CUMUL_NODES = log_kpis(Path(PATH),file_name,Graph,DiGraph,CUMUL_NODES)
        visu_graph(DiGraph,file)
        #subprocess.run(['xterm','-e','vim', f'{PATH}html/Graphs.log'],check=True)
    sys.exit()
