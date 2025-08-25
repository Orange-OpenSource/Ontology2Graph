''' This python script compute some Knowledge Graphs KPIs and display the Graph.
You must pass as an argument the absolute path where are stored the ttl files or the PATH + the
file name for a single one file'''

import os
import sys
import shutil
import logging
import subprocess
from pathlib import Path
from utils.utils_display import visu_graph, populate_graph,log_kpis,set_the_graph

arg = sys.argv[1:]
PATH= arg[0]
ONTOLOGY = os.path.expanduser('../generate_graphs/ontologies/noria_to_check.ttl')
CUMUL_NODES=0

### create new log_html_folder and clean old logs ###
if Path(PATH).is_file():
    log_html_folder = Path(f'{str(Path(PATH).parent)}/log_html/')
else:
    log_html_folder = Path(f'{str(Path(PATH))}/log_html/')

if log_html_folder.exists() and log_html_folder.is_dir():
    shutil.rmtree(log_html_folder)

Path.mkdir(log_html_folder)

log_file=Path(f'{log_html_folder}/Graph_KPIs.log')

### set logger ###
logger = logging.getLogger('Graph_KPI')
handler = logging.FileHandler(log_file)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

if Path(PATH).is_file():

    print('this is a single file')
    file_name=Path(PATH).name
    absolute_file_name=Path(f'{Path(PATH).parent.resolve()}/{file_name}')

    g, Graph, DiGraph = set_the_graph(PATH,log_html_folder)

    populate_graph(g,Graph,DiGraph)
    log_kpis(file_name,Graph,DiGraph,CUMUL_NODES)
    visu_graph(DiGraph,absolute_file_name,log_html_folder)
    #subprocess.run(['xterm', '-e', 'vim', f'{PATH}/html/Graphs.log'],check=True)
    sys.exit()

else :

    all_files = [str(f.resolve()) for f in Path(PATH).iterdir() if f.is_file()]

    for file in all_files :
        print('FILE',file)

        g, Graph, DiGraph = set_the_graph(file,log_html_folder)

        populate_graph(g,Graph,DiGraph)
        CUMUL_NODES = log_kpis(file,Graph,DiGraph,CUMUL_NODES)
        visu_graph(DiGraph,file,log_html_folder)
        #subprocess.run(['xterm','-e','vim', f'{PATH}html/Graphs.log'],check=True)
    sys.exit()
