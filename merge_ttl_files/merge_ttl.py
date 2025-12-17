""" This script merges multiple knowledge graphs (in Turtle format) into a single unified graph \
    using a specified ontology.

Main Features:
- Identifies duplicate nodes and computes their maximum occurrence values across the graphs.
- Merges graphs into one, manages RDF prefixes, and checks the validity of the resulting TTL file.
- Logs the merging process and removes previous log and result files for a clean run.

Usage:
    python merge_ttl.py --path_file <graphs_folder> --ontology <ontology_file>

Arguments:
    path_file:   Absolute path to the folder containing the knowledge graph TTL files.
    ontology:    Path to the ontology TTL file.
"""

from ast import arguments
import utils_merge.utils as utils_merge
import utils_common.utils as utils_common

### Set up argument parser ###
arguments= [("path_file", "Graphs file path"), ("ontology", "Ontology file path")]
args = utils_common.setup_argument_parser("parser", arguments)
path_files=args.path_file
ontology=args.ontology

bad_path_result,log_file,log_file_homonymes,log_file_check_ttl,path_merged,path_duplicate_treated\
    =utils_merge.build_merged_folder_paths_and_files(path_files)

### Set up loggers ###
logger_merge= utils_common.setup_logger(log_file,'merge_log')
logger_homonymes= utils_common.setup_logger(log_file_homonymes,'homonymes_log')
logger_check_ttl= utils_common.setup_logger(log_file_check_ttl,'check_merged_ttl_log')


### Find homonymes nodes and max occurrence value ###
homonymes_nodes = utils_merge.find_homonymes_nodes(path_files,logger_homonymes,ontology)
occ_max = utils_merge.max_node_occ_value(path_files,ontology,logger_homonymes)

### Merge & check ttl files ###
utils_merge.rename_homonyme_in_files(path_duplicate_treated,path_merged,homonymes_nodes,occ_max[0],\
                             logger_merge)

utils_merge.manage_prefix(path_merged)
utils_merge.check_ttl(path_merged,bad_path_result,logger_check_ttl)
