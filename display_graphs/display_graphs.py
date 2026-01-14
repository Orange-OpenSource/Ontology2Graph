''' This python script compute some Knowledge Graphs KPIs and display the Graph.
You must pass as an argument the absolute path where are stored the ttl files or the PATH + the
file name for a single one file'''

from pathlib import Path
from utils import utils_display as utils
from utils_common import utils as utils_common

### set argument parser ###
args = utils_common.setup_argument_parser([("path", "path where files are stored")\
                                ,("ontology", "ontology file path"),("mode", "display mode")])

### initialize cumulative variables ###
CUMUL_NODES=0
CUMUL_DENSITY=0

### create new log_html_folder and clean old logs ###
log_html_folder=utils.create_new_log_html_folder(args.path)
log_file=Path(f'{log_html_folder}/graph_kpi.log')

### set logger ###
logger = utils_common.setup_logger(log_file,'graph_kpi')

### display graphs and compute kpis ###
if Path(args.path).is_file(): 
    file_name=Path(args.path).name
    absolute_file_name=Path(f'{Path(args.path).parent.resolve()}/{file_name}')

    if args.mode=='basic':
        Digraph = utils.prepare_graph_to_display_basic(args.path,log_html_folder,args.ontology)
        utils.visu_graph_basic(Digraph, absolute_file_name, log_html_folder)
        utils.log_kpis_basic(file_name, Digraph, CUMUL_NODES, CUMUL_DENSITY)
    elif args.mode=='advanced':
        Digraph, node_type_lists = utils.prepare_graph_to_display_advanced(args.path,\
                                                                log_html_folder,args.ontology)
        utils.visu_graph_advanced(Digraph,absolute_file_name,log_html_folder,node_type_lists)
        utils.log_kpis_advanced(file_name,Digraph,CUMUL_NODES,CUMUL_DENSITY,node_type_lists)

else :
    all_files = [str(f.resolve()) for f in Path(args.path).iterdir() if f.is_file()]

    for file in all_files :

        if args.mode=='basic':
            Digraph = utils.prepare_graph_to_display_basic(file,log_html_folder,args.ontology)
            utils.visu_graph_basic(Digraph, file, log_html_folder)
            CUMUL_NODES,CUMUL_DENSITY=utils.log_kpis_basic(file,Digraph,CUMUL_NODES,CUMUL_DENSITY)
        elif args.mode=='advanced':
            Digraph, node_type_lists = utils.prepare_graph_to_display_advanced(file,\
                                                                log_html_folder,args.ontology)
            utils.visu_graph_advanced(Digraph, file, log_html_folder,node_type_lists)
            CUMUL_NODES,CUMUL_DENSITY = utils.log_kpis_advanced(file,Digraph,CUMUL_NODES,\
                                                                CUMUL_DENSITY,node_type_lists)

