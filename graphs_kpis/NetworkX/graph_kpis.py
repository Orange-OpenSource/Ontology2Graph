''' This python script compute some Knowledge Graph KPIs '''

import csv
from rdflib import Graph
import networkx as nx

#constant
PATH = "../../graphs_generated_by_models/Noria/"
FILE = "First_graph_noria_2025-06-20_16-20-20_gemini-2.0-flash-001.ttl"

#load the graph
graph = Graph()
graph.parse(f'{PATH}/{FILE}', format="turtle")
#nx_graph = rdflib_to_networkx_multidigraph(graph)
#nx_graph = nx.DiGraph(graph)
nx_graph = nx.MultiDiGraph(graph)

nbr_nodes=nx_graph.number_of_nodes()
nbr_edges=nx_graph.number_of_edges()
nodes=list(nx_graph.nodes())

with open('output.csv', mode='w', newline='',encoding='utf-8') as file:
    writer = csv.writer(file)
    for item in nodes :
        writer.writerow([item])
    file.close()

print(f"Number of nodes: {nbr_nodes}")
print(f"Number of edges: {nbr_edges}")
#print(f"Nodes in the graph: {nodes}")

#Convert ttl file to graphml for Gephi usage
graph.parse(f'{PATH}/{FILE}', format="turtle")

# Serialize to GraphML
graph.serialize(destination='output.graphml', format="xml")

