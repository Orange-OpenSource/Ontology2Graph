# Software Name : Ontologie2Graph
# SPDX-FileCopyrightText: Copyright (c) Orange SA
# SPDX-License-Identifier: BSD-4-Clause
#
# This software is distributed under the BSD 4-Clause "Original" or "Old" License,
# see the "LICENSE" file for more details or <license-url>

""" Knowledge Graph Consistency Checker

This script performs comprehensive consistency checking and reasoning validation on
knowledge graphs by combining them with their corresponding ontologies and applying
formal logical reasoning engines.

The tool supports two primary reasoning engines (HermiT and Pellet) to detect:
- Ontological inconsistencies in the knowledge graph
- Unsatisfiable classes that violate logical constraints
- Structural integrity issues in RDF/TTL graph files

Main Features:
- Single file or batch directory processing
- Ontology-graph concatenation for complete consistency checking
- Support for HermiT and Pellet reasoners
- Comprehensive logging of validation results
- Automatic cleanup of temporary files
- Detection of inconsistent classes equivalent to owl:Nothing

Usage:
    python check_skg.py <graph_path> <ontology_file> <reasoner>

Arguments:
    graph_path:    Path to a single TTL file or directory containing multiple TTL files
    ontology_file: Path to the ontology TTL file used for consistency checking
    reasoner:      Reasoning engine to use ("HermiT" or "Pellet")

Output:
    - Creates a 'check_graph_log' directory in the graph path location
    - Generates detailed log files with consistency check results
    - Console output indicating discovered inconsistencies or validation success

Dependencies:
    - rdflib: For RDF graph parsing and serialization
    - owlready2: For ontology loading and reasoning engine integration
    - pathlib: For cross-platform file path operations

Example:
    python check_skg.py ./graphs/synthetic_graph.ttl ./ontology/schema.ttl HermiT
    python check_skg.py ./graphs_directory/ ./ontology/schema.ttl Pellet

Author: GenGraphLLM Project
License: BSD 4-Clause License"""

import logging
from pathlib import Path
import shutil
import os
import rdflib
from owlready2 import get_ontology,sync_reasoner_hermit,sync_reasoner_pellet
from owlready2 import OwlReadyInconsistentOntologyError,default_world
from utils_common import utils as utils_common

### set argument parser ###
args = utils_common.setup_argument_parser([("path", "path where files are stored")\
                            ,("ontology", "ontology file path"),("reasonner","Pellet or HermiT")])

if args.reasonner not in ["Pellet", "HermiT"]:
    raise ValueError("Reasonner must be either 'Pellet' or 'HermiT'")

### Setup path and files ###
if Path(args.path).is_file():
    path_check_log=Path(f'{Path(args.path).parent}/check_graph_log')
    all_graph_to_check = [args.path]
    path_graph_file=Path(args.path).parent
else :
    path_check_log=Path(f'{args.path}/check_graph_log')
    all_graph_to_check = [f for f in Path(args.path).iterdir() if f.is_file()]

if os.path.exists(path_check_log):
    shutil.rmtree(path_check_log)

os.makedirs(path_check_log)

log_file=Path(f'{path_check_log}/check_graph.log')

### set logger ###
logger_check = utils_common.setup_logger(log_file,'graph_kpi',logging.DEBUG)

### Check each graph ###
CONCAT = f'{Path(f'{os.getcwd()}')}/concat.ttl'
for graph_to_check in all_graph_to_check :
    print(graph_to_check)

    ### Concat ontology and graph in the same file ###
    with open(CONCAT, 'w', encoding='utf-8') as target_file:
        for source_file in [args.ontology,graph_to_check]:
            with open(source_file, 'r', encoding='utf-8') as file_source:
                for line in file_source:
                    target_file.write(line)

    ### Load concatenated graph with RDFLib ###
    skgraph = rdflib.Graph()
    skgraph.parse(f"file://{CONCAT}", format="turtle")

    ### Convert RDFLib graph to OWL/XML format ###
    graph_xml = skgraph.serialize(format="xml")
    encoded_graph = graph_xml.encode('utf-8')

    ### Save the OWL/XML graph to a temporary file ###
    with open(f'temp_graph_{Path(graph_to_check).name}', "wb") as temp_graph_owl:
        temp_graph_owl.write(encoded_graph)

    encoded_graph_to_check=get_ontology(f'file://temp_graph_{Path(graph_to_check).name}').load()

    logger_check.info('##########################################################################')
    logger_check.info('Graph : %s ',Path(graph_to_check).name)

    try:
        with encoded_graph_to_check:
            if args.reasonner=="HermiT":
                sync_reasoner_hermit(debug=0, keep_tmp_file=True,
                                      ignore_unsupported_datatypes = True)
            if args.reasonner=="Pellet":
                sync_reasoner_pellet(debug=0, keep_tmp_file=True)

    except OwlReadyInconsistentOntologyError as OntoE:
        print(f'\nOwlReadyInconsistentOntologyError detected by {args.reasonner} for '
              f'{Path(graph_to_check).name}')
        logger_check.info('OwlReadyInconsistentOntologyError detected by : %s \n',args.reasonner)
        logger_check.info(OntoE)

    except OverflowError as e: #system ressource limits reach
        print(f"\nOverFlowError : {e}")
        logger_check.info('OverFlowError : %s',e)

    else :
        print(f'\nNo inconsistent Ontology errors detected by {args.reasonner} for '
              f'{Path(graph_to_check).name}')
        logger_check.info('No inconsistent Ontology errors found by %s ',args.reasonner)

    ### List classes inferred equivalent to owl:Nothing (unsatisfiable classes) ###
    unsat = list(default_world.inconsistent_classes())
    if unsat:
        print(f'inconsistent classes found by {args.reasonner} :\n')
        for c in unsat:
            print(" - \n", c)
            logger_check.info('inconsistent classes found by %s',args.reasonner)
            logger_check.info(' %s',c)
    else:
        print(f'No inconsistent classes found by {args.reasonner} for {Path(graph_to_check).name}')
        logger_check.info('No inconsistent classes found by %s \n',args.reasonner)

    ### Remove CONCAT file ###
    if Path(CONCAT).is_file():
        os.remove(Path(CONCAT))
    ### Remove temp_graph_owl ###
    if Path(f'{Path(f'{os.getcwd()}')}/temp_graph_{Path(graph_to_check).name}').is_file():
        os.remove(Path(f'{Path(f'{os.getcwd()}')}/temp_graph_{Path(graph_to_check).name}'))
