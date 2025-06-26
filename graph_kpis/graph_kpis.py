''' This python script compute some Knowledge Graph KPIs '''
from rdflib.extras.external_graph_libs import *
from rdflib import Graph, URIRef, Literal
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt


#constant
PATH = "../comparison_model_results/Noria/"

#load the graph
graph = Graph()
graph.parse(f'{PATH}/First_graph_noria_2025-06-20_16-20-20_gemini-2.0-flash-001.ttl', format="turtle")
#nx_graph = rdflib_to_networkx_multidigraph(graph)
nx_graph = nx.DiGraph(graph)

nbr_nodes=nx_graph.number_of_nodes()
nbr_edges=nx_graph.number_of_edges()
nodes=list(nx_graph.nodes())


print(f"Number of nodes: {nbr_nodes}")
print(f"Number of edges: {nbr_edges}")
print(f"Nodes in the graph: {nodes}")





