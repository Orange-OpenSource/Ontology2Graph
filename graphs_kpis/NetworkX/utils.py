'''list of function to be used '''

import webbrowser
import os
from pyvis.network import Network

def remove_pred_obj(expr, graph, predi, obje):
    '''remove predicate and target object of an edge'''
    edges_to_remove = [(u, v) for u, v, attr in graph.edges(data=True)
                         if attr.get(expr) == predi and v == obje]
    return graph.remove_edges_from(edges_to_remove)

def get_last_folder_part(string, sep_char):
    """get last part of a folder string"""
    string_parts=string.split(sep_char)
    last_part=string_parts[len(string_parts)-1]
    return last_part

def retreive_datatype_properties(ontology):
    '''create a list of all the data type properties from the ontologie'''

    index_list=[]
    dtprop=[]
    dtproperties=[]

    #build index list of DatatypeProperty
    with open(f'{ontology}', 'r',encoding='utf-8') as file:
        for index, line in enumerate(file, start=1):
            if 'DatatypeProperty' in line :
                index_list.append(index-1)
    file.close()

    #retreive DatatypeProperties based on index list
    with open(f'{ontology}', 'r',encoding='utf-8') as file:
        for index, line in enumerate(file, start=1):
            if index in index_list:
                dtprop.append(line.strip())
                print(line.strip())
    file.close()

    #clean DatatypeProperties
    for dtp in dtprop:
        dtp=dtp.replace('noria:',"")
        dtproperties.append(dtp)
    return dtproperties

def dysplay_graph(graph):
    '''dysplay the graph'''

    net = Network(height="840px", width="100%", bgcolor="#222222", font_color="white",
                  directed=True,neighborhood_highlight=True)

    net.barnes_hut()
    net.from_nx(graph)
    #net.show_buttons(filter_=['physics'])

    OUTPUTFILE= "mon_graphe_de_test.html"
    net.save_graph(OUTPUTFILE)
    full_path=os.path.abspath(OUTPUTFILE)
    print('full path',full_path)

    #webbrowser.open(f'file://///wsl.localhost/Ubuntu-24.04{full_path}',autoraise=True)
    webbrowser.open(full_path,autoraise=True)
