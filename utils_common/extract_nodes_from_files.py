
#!/usr/bin/env python3
# Software Name : Ontologie2Graph
# SPDX-FileCopyrightText: Copyright (c) Orange SA
# SPDX-License-Identifier: BSD-4-Clause
#
# This software is distributed under the BSD 4-Clause "Original" or "Old" License,
# see the "LICENSE" file for more details or <license-url>

''' Extract and Export Graph Nodes from TTL Files

This script parses a Turtle (TTL) RDF file to extract meaningful graph nodes, 
excluding metadata properties, and exports them to a CSV file for further analysis.

The script performs the following operations:
1. Parses a TTL file using RDFLib to extract RDF triples
2. Filters out metadata predicates (labels, types, descriptions, etc.)
3. Excludes datatype properties defined in the ontology
4. Creates a directed graph using NetworkX with filtered relationships
5. Exports the resulting nodes to a CSV file

Usage:
    python extract_nodes_from_files.py <ttl_file_path>

Arguments:
    ttl_file_path: Path to the Turtle (.ttl) file to process

Output:
    Creates a 'nodes.csv' file in the current working directory containing 
    one node name per row.

Filtered Predicates:
    - label: Node labels and naming properties
    - type: RDF type declarations
    - inScheme: SKOS concept scheme relationships  
    - description: Descriptive text properties
    - comment: Comment annotations
    - All datatype properties defined in the Noria ontology

Dependencies:
    - rdflib: For RDF/Turtle file parsing
    - networkx: For graph structure creation and manipulation
    - csv: For CSV file generation
    - pathlib: For cross-platform path handling
    - utils_common.utils: For ontology object retrieval

Example:
    python extract_nodes_from_files.py /path/to/graph.ttl
    # Creates nodes.csv with extracted node names'''


import sys
from os import getcwd
import csv
from pathlib import Path
import rdflib
import networkx as nx
from utils_common.utils import retreive_onto_object

arg = sys.argv[1:]
file= arg[0]

g = rdflib.Graph()
g.parse(file, format="turtle")

nx_graph = nx.DiGraph()

ONTO='/home/pdooze/DIGITAL_TWIN/gengraphllm/generate_ttl_files/ontologies/Noria.ttl'
### retreive datatype properties (literals) from ontology ###
datatypeproperties=retreive_onto_object(ONTO,'DatatypeProperty')

### populate the graph ###
for subj, pred, obj in g:
    last_part_pred=Path(str(pred)).stem

    if ('label' in last_part_pred) or ('type' in last_part_pred) or\
        ('inScheme' in last_part_pred) or ('description' in last_part_pred) or\
            ('comment' in last_part_pred) or (last_part_pred in datatypeproperties):
        pass
    else :
        last_part_subj=Path(str(subj)).name
        last_part_obj=Path(str(obj)).name
        nx_graph.add_edge(str(last_part_subj),str(last_part_obj),label=str(last_part_pred))

nodes=list(nx_graph.nodes)

with open(f'{getcwd()}/nodes.csv', 'w', encoding='utf-8',newline='') as f:
    writer = csv.writer(f)
    for item in nodes:
        writer.writerow([item])
    f.close()
