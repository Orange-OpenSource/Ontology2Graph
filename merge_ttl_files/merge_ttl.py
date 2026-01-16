# Software Name : Ontologie2Graph
# SPDX-FileCopyrightText: Copyright (c) Orange SA
# SPDX-License-Identifier: BSD-4-Clause
#
# This software is distributed under the BSD 4-Clause "Original" or "Old" License,
# see the "LICENSE" file for more details or <license-url>

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

#from ast import arguments
import utils_merge.utils as utils_merge
from utils_common import utils as utils_common

### Set up argument parser ###
args = utils_common.setup_argument_parser([("path_file", "Graphs file path"),\
                                            ("ontology", "Ontology file path")])
path_files = args.path_file
ontology = args.ontology

### build path & files ###
bad_path_result,log_file,log_file_homonymes,log_file_check_ttl_merged,path_merged,\
    path_duplicate_treated = utils_merge.build_merged_folder_paths_and_files(path_files)

### Set up loggers ###
logger_merge = utils_common.setup_logger(log_file,'merge_log')
logger_homonymes = utils_common.setup_logger(log_file_homonymes,'homonymes_log')
logger_check_ttl_merged = utils_common.setup_logger(log_file_check_ttl_merged,\
    'check_merged_ttl_log')

### Find homonymes nodes and compute max occurrence value ###
homonymes_nodes_and_occurence = utils_merge.find_homonymes_nodes(path_files,logger_homonymes,\
                                                                 ontology)

logger_merge.info('homonymes_nodes_and_occurence: %s', homonymes_nodes_and_occurence)
MAX_HOMONYME_NAME = max(homonymes_nodes_and_occurence, key=lambda x: \
    homonymes_nodes_and_occurence.get(x, 0)) if homonymes_nodes_and_occurence else None
MAX_HOMONYME_VALUE = homonymes_nodes_and_occurence[MAX_HOMONYME_NAME] if MAX_HOMONYME_NAME else \
    None

homonymes_nodes_list = list(homonymes_nodes_and_occurence.keys())

utils_merge.rename_and_merge(path_duplicate_treated,path_merged,homonymes_nodes_and_occurence,\
    MAX_HOMONYME_VALUE,logger_merge)

### manage merged ttl files prefixes ###
utils_merge.manage_prefix(path_merged)

### check ttl files validity ###
utils_common.check_ttl(path_merged,bad_path_result,logger_check_ttl_merged)
