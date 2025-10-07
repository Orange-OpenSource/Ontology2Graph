''' This python script check the consistency of synthetic knowlege graph with his ontology
You have to pass as parameter the graph and ontologie location '''

import argparse
import subprocess
import rdflib
import owlready2
parser = argparse.ArgumentParser()
parser.add_argument("graph")
parser.add_argument("ontology")
args = parser.parse_args()

graph=args.graph
ontology=args.ontology

# Parse the Turtle file with RDFLib
ontol = rdflib.Graph()
ontol.parse(f"file://{ontology}", format="turtle")

skgraph = rdflib.Graph()
skgraph.parse(f"file://{graph}", format="turtle")

# Convert RDFLib ontology to OWL/XML format
owl_xml = ontol.serialize(format="xml")
encoded_onto = owl_xml.encode('utf-8')

# Convert RDFLib graph to OWL/XML format
graph_xml = skgraph.serialize(format="xml")
encoded_graph = graph_xml.encode('utf-8')

# Save the OWL/XML ontology to a temporary file
with open("temp_ontology.owl", "wb") as f:
    f.write(encoded_onto)

# Save the OWL/XML graph to a temporary file
with open("temp_graph.owl", "wb") as f:
    f.write(encoded_graph)

# Load the OWL/XML ontology with owlready2
onto = owlready2.get_ontology("file://temp_ontology.owl").load()

graph = owlready2.get_ontology("file://temp_graph.owl").load()

# Query the ontology
for cls in onto.classes():
    print(cls)

#SKG = owlready2.get_ontology(graph).load()

# Sync the reasoner with HermiT
with onto:
    try:
        output = subprocess.check_output(owlready2.sync_reasoner_hermit(infer_property_values=True), stderr=subprocess.STDOUT)
        print(output.decode('utf-8'))  # Print the output from HermiT
    except subprocess.CalledProcessError as e:
        print(e.output.decode('utf-8'))  # Print the error output from HermiT
        raise
    owlready2.sync_reasoner_hermit(infer_property_values=True)
   

# Check for inconsistencies
#inconsistencies = []
#for individual in ontology.individuals():
#    if individual.is_a(owlready2.Thing):
#        inconsistencies.append(individual)

#if inconsistencies:
#    print("Inconsistencies found:")
#    for individual in inconsistencies:
#        print(individual)
#else:
#    print("The knowledge graph is consistent with the ontology schema.")
