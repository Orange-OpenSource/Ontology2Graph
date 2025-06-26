''' This python script compute some Knowledge Graph KPIs '''
from rdflib import Graph
import networkx as nx
import csv


#constant
PATH = "../../comparison_model_results/Noria/"
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

with open('output.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    for item in nodes:
            writer.writerow([item])

print(f"Number of nodes: {nbr_nodes}")
print(f"Number of edges: {nbr_edges}")
#print(f"Nodes in the graph: {nodes}")
