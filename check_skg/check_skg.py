''' This python script check the consistency of synthetic knowlege graph with his ontology
You have to pass as parameter the graph and ontologie location '''

import logging
from pathlib import Path
import argparse
import sys
import os
import rdflib
import owlready2

#logging.basicConfig(
#    level=logging.DEBUG,
#    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#)
#owlready2.set_log_level(4)

parser = argparse.ArgumentParser()
parser.add_argument("graph")
parser.add_argument("ontology")
args = parser.parse_args()

#owlready2.JAVA_MEMORY = "4G"  # Set to 4 GB or more as needed

graph=args.graph
ontology=args.ontology

path=Path(f'{os.getcwd()}')
CONCAT = f'{path}/concat.ttl'

#concat ontology and graph in the same file

with open(CONCAT, 'w', encoding='utf-8') as target_file:
    for source_file in [ontology,graph]:
        with open(source_file, 'r', encoding='utf-8') as f:
            for line in f:
                target_file.write(line)

skgraph = rdflib.Graph()

skgraph.parse(f"file://{CONCAT}", format="turtle")

# Convert RDFLib graph to OWL/XML format
graph_xml = skgraph.serialize(format="xml")
encoded_graph = graph_xml.encode('utf-8')

# Save the OWL/XML graph to a temporary file
with open("temp_graph.owl", "wb") as f:
    f.write(encoded_graph)

OUTPUT_LOG = f'{path}/owlready_output.log'
ERROR_LOG = f'{path}/owlready_error.log'

if os.path.exists(OUTPUT_LOG):
    os.remove(OUTPUT_LOG)

if os.path.exists(ERROR_LOG):
    os.remove(ERROR_LOG)

sys.stdout = open('owlready_output.log', 'a', encoding='utf-8')
sys.stderr = open('owlready_error.log', 'a', encoding='utf-8')

graph = owlready2.get_ontology("file://temp_graph.owl").load()
owlready2.sync_reasoner()
