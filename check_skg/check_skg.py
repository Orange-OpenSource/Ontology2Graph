''' This python script check the consistency of synthetic knowlege graph with his ontology
You have to pass as parameter the graph and ontologie location '''

import logging
from pathlib import Path
import argparse
import sys
import os
import rdflib
from owlready2 import get_ontology,sync_reasoner_hermit,sync_reasoner_pellet,owl,OwlReadyInconsistentOntologyError,default_world

parser = argparse.ArgumentParser()
parser.add_argument("graph")
parser.add_argument("ontology")
args = parser.parse_args()

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

graph = get_ontology("file://temp_graph.owl").load()

#sys.stdout = open('owlready_output.log', 'a', encoding='utf-8')
#sys.stderr = open('owlready_error.log', 'a', encoding='utf-8')   

try:
    with graph:
        #sync_reasoner_hermit(debug=2, keep_tmp_file=True,infer_property_values=True)
        sync_reasoner_pellet(debug=2, keep_tmp_file=True,
                             infer_property_values=True, infer_data_property_values=True)
except OwlReadyInconsistentOntologyError:
    print("HermiT Reasoner reported an inconsistency (OwlReadyInconsistentOntologyError).")
except Exception as e:
    print("Reasoner error:", e)

# list classes inferred equivalent to owl:Nothing (unsatisfiable classes)
unsat = list(default_world.inconsistent_classes())
if unsat:
    print("inconsistent classes found:")
    for c in unsat:
        print(" -", c)
else:
    print("No inconsistent classes found.")

