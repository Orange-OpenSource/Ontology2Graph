''' This python script compute some Knowledge Graphs KPIs and display the Graph.
You must pass as an argument the absolute path where are stored the ttl files or the PATH + the
file name for a single one file'''

import os
import sys
import shutil
import logging
from pathlib import Path
from utils.utils_display import visu_graph, prepare_graph_to_display, log_kpis

arg = sys.argv[1:]
PATH= arg[0]
ONTOLOGY = os.path.expanduser('../generate_ttl_files/ontologies/Noria.ttl')
CUMUL_NODES=0
CUMUL_DENSITY=0

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
    Digraph, node_type_lists = prepare_graph_to_display(PATH,log_html_folder,ONTOLOGY)
    log_kpis(file_name, Digraph, CUMUL_NODES, CUMUL_DENSITY, node_type_lists)
    visu_graph(Digraph, absolute_file_name, log_html_folder, node_type_lists)

    sys.exit()

else :

    all_files = [str(f.resolve()) for f in Path(PATH).iterdir() if f.is_file()]
    print(all_files)

    for file in all_files :

        Digraph, node_type_lists = prepare_graph_to_display(file, log_html_folder, ONTOLOGY)
        CUMUL_NODES, CUMUL_DENSITY = log_kpis(file, Digraph, CUMUL_NODES, CUMUL_DENSITY,\
                                               node_type_lists)
        visu_graph(Digraph, file, log_html_folder, node_type_lists)

    sys.exit()
