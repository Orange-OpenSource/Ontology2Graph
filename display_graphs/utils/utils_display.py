'''list of function to be used '''

import logging
import webbrowser
import os
from pathlib import Path
from rdflib import URIRef, Literal, Namespace,BNode
from pyvis.network import Network
import networkx as nx
from networkx.classes.function import density, degree_histogram, number_of_selfloops
from networkx import average_degree_connectivity
import rdflib

def remove_pred_obj(expr, graph, predi, obje):
    '''remove predicate and target object of an edge'''
    edges_to_remove = [(u, v) for u, v, attr in graph.edges(data=True)
                         if attr.get(expr) == predi and v == obje]
    return graph.remove_edges_from(edges_to_remove)

def get_last_folder_part(string, sep_char):
    """get last part of a folder string"""
    string_parts=string.split(sep_char)
    last_part=string_parts[len(string_parts)-1]
    if last_part=='':
        last_part=string_parts[len(string_parts)-2]
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
                #print(line.strip())
    file.close()

    #clean DatatypeProperties
    for dtp in dtprop:
        dtp=dtp.replace('noria:',"")
        dtproperties.append(dtp)
    #print(dtproperties)
    return dtproperties

def visu_graph(graph,file,html_folder):
    '''display the graph with enhanced visualization settings'''

    # Create network with responsive sizing
    net = Network(height="95vh", width="100%", bgcolor="#1a1a1a", font_color="white",
                  directed=True)
    net.barnes_hut()

    # Convert NetworkX graph to pyvis first
    net.from_nx(graph)

    # Improved physics settings for better stability and readability
    net.set_options("""{
        "physics": {
            "solver": "barnesHut",
            "barnesHut": {
                "gravitationalConstant": -50000,
                "centralGravity": 0,
                "springLength": 500,
                "springConstant": 0.01,
                "damping": 0.2,
                "avoidOverlap": 0.5
                },
            "stabilization": {
                "enabled": true,
                "iterations": 200,
                "updateInterval": 25
                }
            },
        "edges":{
            "smooth": {
                "enabled": true,
                "type": "continuous"
                },
            "arrows": {
                "to": {
                    "enabled": true,
                    "scaleFactor": 0.5
                    }
                },
            "font": {
                "size": 12,
                "align": "middle",
                "background": "#1a1a1a",
                "strokeWidth": 0,
                "color": "#ffffff"
                },
            "width": 2
            },
        "nodes": {
            "shape": "dot",
            "size": 16,
            "font": {
                "size": 14,
                "face": "arial",
                "color": "#ffffff"
                },
            "borderWidth": 2,
            "borderWidthSelected": 3
            },
        "interaction": {
            "hover": true,
            "tooltipDelay": 100,
            "hideEdgesOnDrag": true,
            "navigationButtons": true,
            "keyboard": {
                "enabled": true
                }
            },
        "configure": {
            "enabled": true,
            "filter": "physics"
            }
        }""")

    # Color code edges: cyan for entity-to-entity, green for entity-to-literal
    edge_colors = {
        'entity_to_entity': '#00d4ff',  # Cyan for entity relationships
        'entity_to_literal': '#00cc66'   # Green for literal/datatype properties
    }

    # Apply colors and styling to edges based on whether they connect to literals or entities
    for edge in net.edges:
        edge_label = edge.get('label', '')
        # Get edge data from original graph to determine type
        edge_type = 'entity_to_entity'  # default
        for u, v, data in graph.edges(data=True):
            if (edge.get('from') == u or edge.get('from') == str(u)) and \
               (edge.get('to') == v or edge.get('to') == str(v)):
                edge_type = data.get('edge_type', 'entity_to_entity')
                break

        edge['color'] = edge_colors.get(edge_type, '#888888')
        # Tooltip shows relationship type and category
        edge['title'] = f"{edge_label} ({edge_type.replace('_', ' ')})"

    # Calculate node sizes based on degree (connectivity)
    if len(graph.nodes()) > 0:
        degrees = dict(graph.degree())
        max_degree = max(degrees.values()) if degrees else 1
        min_degree = min(degrees.values()) if degrees else 0
        degree_range = max_degree - min_degree if max_degree > min_degree else 1

        # Identify literal nodes (nodes that are targets of entity_to_literal edges)
        literal_nodes = set()
        for u, v, data in graph.edges(data=True):
            if data.get('edge_type') == 'entity_to_literal':
                literal_nodes.add(v)

        # Apply node sizes and colors (blue for entities, green for literals)
        for node in net.nodes:
            node_id = node['id']
            if node_id in degrees:
                degree = degrees[node_id]
                # Scale node size between 10 and 40 based on degree
                node['size'] = 10 + (30 * (degree - min_degree) / degree_range)

                # Check if this is a literal node
                if node_id in literal_nodes:
                    # Green color for literal nodes
                    node['color'] = {
                        'border': '#ffffff',
                        'background': '#00cc66',
                        'highlight': {
                            'border': '#ffff00',
                            'background': '#00ff88'
                        }
                    }
                else:
                    # Blue color for entity nodes
                    node['color'] = {
                        'border': '#ffffff',
                        'background': '#0066cc',
                        'highlight': {
                            'border': '#ffff00',
                            'background': '#0088ff'
                        }
                    }
                node['title'] = f"{node_id}\nDegree: {degree}"

    os.makedirs(html_folder,exist_ok=True)

    html_file = f'{html_folder}/{Path(file).stem}.html'

    net.save_graph(html_file)

    # Add custom JavaScript for node selection and filtering
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Insert custom JavaScript before closing body tag
    custom_js = f"""
    <script type=\"text/javascript\">
        // Track literal nodes
        var literalNodeIds = [];
        var literalEdgeIds = [];
        var literalsVisible = true;
        var visibleNodes = [];  // Track currently visible nodes (for filtered view)
        var isFiltered = false;  // Track if we're in a filtered view
        var selectedNodeId = null;
        var showConnected = true; // For the new button

        // Identify literal nodes and edges from the graph data
        var allEdges = edges.get();
        allEdges.forEach(function(edge) {{
            if (edge.title && edge.title.includes('entity to literal')) {{
                literalNodeIds.push(edge.to);
                literalEdgeIds.push(edge.id);
            }}
        }});

        // Function to toggle literal visibility
        function toggleLiterals() {{
            literalsVisible = !literalsVisible;
            var btn = document.getElementById('toggleLiteralsBtn');

            if (isFiltered) {{
                // Only toggle literals in the visible/filtered subgraph
                var visibleLiterals = literalNodeIds.filter(function(id) {{
                    return visibleNodes.indexOf(id) !== -1;
                }});

                var visibleLiteralEdges = literalEdgeIds.filter(function(edgeId) {{
                    var edge = edges.get(edgeId);
                    return visibleNodes.indexOf(edge.from) !== -1 || visibleNodes.indexOf(edge.to) !== -1;
                }});

                // Update only visible literal nodes
                visibleLiterals.forEach(function(nodeId) {{
                    nodes.update({{id: nodeId, hidden: !literalsVisible}});
                }});

                // Update only visible literal edges
                visibleLiteralEdges.forEach(function(edgeId) {{
                    edges.update({{id: edgeId, hidden: !literalsVisible}});
                }});
            }} else {{
                // Toggle all literals
                literalNodeIds.forEach(function(nodeId) {{
                    nodes.update({{id: nodeId, hidden: !literalsVisible}});
                }});

                literalEdgeIds.forEach(function(edgeId) {{
                    edges.update({{id: edgeId, hidden: !literalsVisible}});
                }});
            }}

            // Update button text
            btn.innerHTML = literalsVisible ? 'Hide Literals' : 'Show Literals';
            btn.style.backgroundColor = literalsVisible ? 'rgba(204, 0, 0, 0.8)' : 'rgba(0, 153, 0, 0.8)';
        }}

        // Button to show/hide connected nodes (appears on node select)
        var toggleConnectedBtn = document.createElement('button');
        toggleConnectedBtn.id = 'toggleConnectedBtn';
        toggleConnectedBtn.innerHTML = 'Hide Connected Nodes';
        toggleConnectedBtn.style.position = 'fixed';
        toggleConnectedBtn.style.top = '50px';
        toggleConnectedBtn.style.left = '10px';
        toggleConnectedBtn.style.backgroundColor = 'rgba(0, 102, 204, 0.8)';
        toggleConnectedBtn.style.color = 'white';
        toggleConnectedBtn.style.padding = '10px 20px';
        toggleConnectedBtn.style.border = 'none';
        toggleConnectedBtn.style.borderRadius = '5px';
        toggleConnectedBtn.style.cursor = 'pointer';
        toggleConnectedBtn.style.zIndex = '1000';
        toggleConnectedBtn.style.fontFamily = 'Arial';
        toggleConnectedBtn.style.fontSize = '14px';
        toggleConnectedBtn.style.fontWeight = 'bold';
        toggleConnectedBtn.style.display = 'none';
        document.body.appendChild(toggleConnectedBtn);

        // Add Edge Types Legend below the button
        var legendDiv = document.createElement('div');
        legendDiv.id = 'legend';
        legendDiv.style.position = 'fixed';
        legendDiv.style.top = '100px';
        legendDiv.style.left = '10px';
        legendDiv.style.backgroundColor = 'rgba(0,0,0,0.85)';
        legendDiv.style.color = 'white';
        legendDiv.style.padding = '15px';
        legendDiv.style.borderRadius = '8px';
        legendDiv.style.zIndex = '1000';
        legendDiv.style.fontFamily = 'Arial';
        legendDiv.style.fontSize = '12px';
        legendDiv.innerHTML = '<b>Edge Types Legend:</b><br>' +
            '<div style="margin: 5px 0;"><span style="display: inline-block; width: 30px; height: 3px; background-color: {edge_colors["entity_to_entity"]}; margin-right: 8px; vertical-align: middle;"></span><span>Entity to Entity</span></div>' +
            '<div style="margin: 5px 0;"><span style="display: inline-block; width: 30px; height: 3px; background-color: {edge_colors["entity_to_literal"]}; margin-right: 8px; vertical-align: middle;"></span><span>Entity to Literal</span></div>';
        document.body.appendChild(legendDiv);

        function updateToggleConnectedBtn(show) {{
            toggleConnectedBtn.style.display = show ? 'block' : 'none';
        }}

        function toggleConnectedNodes() {{
            if (selectedNodeId === null) return;
            var connectedNodes = network.getConnectedNodes(selectedNodeId);
            if (showConnected) {{
                // Hide connected entity nodes (except selected), keep literals visible
                connectedNodes.forEach(function(nodeId) {{
                    if (nodeId !== selectedNodeId && literalNodeIds.indexOf(nodeId) === -1) {{
                        nodes.update({{id: nodeId, hidden: true}});
                    }}
                }});
                toggleConnectedBtn.innerHTML = 'Show Connected Nodes';
            }} else {{
                // Show connected nodes (entities and literals)
                connectedNodes.forEach(function(nodeId) {{
                    nodes.update({{id: nodeId, hidden: false}});
                }});
                toggleConnectedBtn.innerHTML = 'Hide Connected Nodes';
            }}
            showConnected = !showConnected;
        }}
        toggleConnectedBtn.onclick = toggleConnectedNodes;

        // Add node selection functionality to hide unconnected nodes
        network.on("click", function(params) {{
            if (params.nodes.length > 0) {{
                selectedNodeId = params.nodes[0];
                var connectedNodes = network.getConnectedNodes(selectedNodeId);
                var allNodes = nodes.get({{returnType:"Object"}});
                var allEdges = edges.get({{returnType:"Object"}});

                // Add the selected node to connected nodes
                connectedNodes.push(selectedNodeId);

                // Store visible nodes for literal toggling
                visibleNodes = connectedNodes;
                isFiltered = true;

                // Hide unconnected nodes and edges
                for (var nodeId in allNodes) {{
                    if (connectedNodes.indexOf(nodeId) === -1) {{
                        nodes.update({{id: nodeId, hidden: true}});
                    }} else {{
                        // Only show if it's not a literal or if literals are visible
                        var isLiteral = literalNodeIds.indexOf(nodeId) !== -1;
                        if (isLiteral && !literalsVisible) {{
                            nodes.update({{id: nodeId, hidden: true}});
                        }} else {{
                            nodes.update({{id: nodeId, hidden: false}});
                        }}
                    }}
                }}

                // Hide edges not connected to selected node
                for (var edgeId in allEdges) {{
                    var edge = allEdges[edgeId];
                    if (connectedNodes.indexOf(edge.from) === -1 || connectedNodes.indexOf(edge.to) === -1) {{
                        edges.update({{id: edgeId, hidden: true}});
                    }} else {{
                        // Only show if it's not a literal edge or if literals are visible
                        var isLiteralEdge = literalEdgeIds.indexOf(edgeId) !== -1;
                        if (isLiteralEdge && !literalsVisible) {{
                            edges.update({{id: edgeId, hidden: true}});
                        }} else {{
                            edges.update({{id: edgeId, hidden: false}});
                        }}
                    }}
                }}
                // Show the toggle connected button
                updateToggleConnectedBtn(true);
                showConnected = true;
                toggleConnectedBtn.innerHTML = 'Hide Connected Nodes';
            }} else {{
                // If click on empty space, hide the button
                updateToggleConnectedBtn(false);
                selectedNodeId = null;
            }}
        }});

        // Double-click to show all nodes again (respecting literal visibility)
        network.on("doubleClick", function(params) {{
            var allNodes = nodes.get({{returnType:"Object"}});
            var allEdges = edges.get({{returnType:"Object"}});

            isFiltered = false;
            visibleNodes = [];
            selectedNodeId = null;
            updateToggleConnectedBtn(false);

            // Show all nodes
            for (var nodeId in allNodes) {{
                // Check if it's a literal and respect the literal visibility setting
                if (literalNodeIds.indexOf(nodeId) !== -1) {{
                    nodes.update({{id: nodeId, hidden: !literalsVisible}});
                }} else {{
                    nodes.update({{id: nodeId, hidden: false}});
                }}
            }}

            // Show all edges
            for (var edgeId in allEdges) {{
                // Check if it's a literal edge and respect the literal visibility setting
                if (literalEdgeIds.indexOf(edgeId) !== -1) {{
                    edges.update({{id: edgeId, hidden: !literalsVisible}});
                }} else {{
                    edges.update({{id: edgeId, hidden: false}});
                }}
            }}
        }});

        // Add toggle literals button
        var toggleBtn = document.createElement('button');
        toggleBtn.id = 'toggleLiteralsBtn';
        toggleBtn.innerHTML = 'Hide Literals';
        toggleBtn.style.position = 'fixed';
        toggleBtn.style.top = '10px';
        toggleBtn.style.left = '10px';
        toggleBtn.style.backgroundColor = 'rgba(204, 0, 0, 0.8)';
        toggleBtn.style.color = 'white';
        toggleBtn.style.padding = '10px 20px';
        toggleBtn.style.border = 'none';
        toggleBtn.style.borderRadius = '5px';
        toggleBtn.style.cursor = 'pointer';
        toggleBtn.style.zIndex = '1000';
        toggleBtn.style.fontFamily = 'Arial';
        toggleBtn.style.fontSize = '14px';
        toggleBtn.style.fontWeight = 'bold';
        toggleBtn.onclick = toggleLiterals;
        document.body.appendChild(toggleBtn);

        // Add instructions overlay
        var instructions = document.createElement('div');
        instructions.style.position = 'fixed';
        instructions.style.top = '10px';
        instructions.style.right = '10px';
        instructions.style.backgroundColor = 'rgba(0,0,0,0.8)';
        instructions.style.color = 'white';
        instructions.style.padding = '15px';
        instructions.style.borderRadius = '5px';
        instructions.style.zIndex = '1000';
        instructions.style.fontFamily = 'Arial';
        instructions.style.fontSize = '12px';
        instructions.innerHTML = '<b>Graph Controls:</b><br>• Click node: Show only connected nodes<br>• Double-click: Show all nodes<br>• When a node is selected, use the "Hide Connected Nodes" button to hide/show its neighbors.';
        document.body.appendChild(instructions);

    </script>
    """

    html_content = html_content.replace('</body>', custom_js + '</body>')

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    webbrowser.open(html_file,autoraise=True)

def prepare_graph_to_display(file,log_html_folder,ontology):
    '''set the graph and remove literal and other expression from the graph in order to keep only
    the real nodes and their relation to display, log some inforations'''

    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    skos = Namespace("http://www.w3.org/2004/02/skos/core#")

    ### set logger ###
    log_file = f'{Path(log_html_folder)}/URI_and_LITERAL.log'
    log_file_sorted = f'{Path(log_html_folder)}/URI_and_LITERAL_sorted.log'

    logger_file1 = logging.getLogger('URI_and_LITERAL')
    handler_file1 = logging.FileHandler(log_file)
    logger_file1.setLevel(logging.INFO)
    logger_file1.addHandler(handler_file1)

    ### set the graph based on the turtle file and log some infos ###
    digraph = nx.DiGraph()
    g = rdflib.Graph()
    g.parse(f'{file}', format='turtle')

    logger_file1.info('##################################################')
    logger_file1.info('%s',file)

    ### populate graph with nodes and relations (including literals) ###
    for subj, pred, obj in g:

        short_pred=Path(pred).name
        short_subj=Path(subj).name
        dtp = retreive_datatype_properties(ontology)

        # Entity-to-entity relationships
        if (
            isinstance(subj, URIRef)
            and isinstance(obj, URIRef)
            and (pred != rdf.type)
            and (pred != skos.inScheme)
            and (pred != rdfs.isDefinedBy)
            and (short_pred not in dtp)
        ):
            short_obj = Path(obj).name
            digraph.add_edge(
                str(short_subj),
                str(short_obj),
                label=str(short_pred),
                edge_type='entity_to_entity',
            )
            logger_file1.info('URIRef Subject : %s', subj)

        # Entity-to-literal relationships (datatype properties)
        if (
            isinstance(subj, URIRef)
            and isinstance(obj, Literal)
            and (pred != rdf.type)
            and (pred != skos.inScheme)
            and (pred != rdfs.isDefinedBy)
        ):
            # Create a label for the literal value (truncate if too long)
            literal_str = str(obj)[:50] + ('...' if len(str(obj)) > 50 else '')
            literal_node = f"{literal_str}"
            digraph.add_edge(
                str(short_subj),
                literal_node,
                label=str(short_pred),
                edge_type='entity_to_literal',
            )
            logger_file1.info('Literal Object : %s', obj)

        # Blank nodes
        if (
            isinstance(subj, BNode)
            and (pred != rdf.type)
            and (pred != skos.inScheme)
        ):
            logger_file1.info('Blank Node Subject :%s', subj)
            for subjbn, predbn in g.subject_predicates(subj):
                short_subjbn = Path(subjbn).name
                short_predbn = Path(predbn).name
                if isinstance(obj, URIRef):
                    short_obj = Path(obj).name
                    digraph.add_edge(
                        str(short_subjbn),
                        str(short_obj),
                        label=str(short_predbn),
                        edge_type='entity_to_entity',
                    )
                elif isinstance(obj, Literal):
                    literal_str = str(obj)[:50] + ('...' if len(str(obj)) > 50 else '')
                    digraph.add_edge(
                        str(short_subjbn),
                        literal_str,
                        label=str(short_predbn),
                        edge_type='entity_to_literal',
                    )
                logger_file1.info(
                    'Blank Node Subject :%s,Predicate :%s,Object : %s',
                    short_subjbn,
                    short_predbn,
                    obj,
                )

    ### log nodes and Literals ###
    logger_file1.info('##################################################')
    logger_file1.info('%s',file)
    for s, p, o in g:
        if isinstance(s, URIRef):
            logger_file1.info('URIRef Subject : %s',s)
        if isinstance(o, Literal):
            logger_file1.info('Literal Object : %s',o)
        if isinstance(s,BNode):
            logger_file1.info('BNode Subject : %s',s)
    logger_file1.info('##################################################')

    ## sort and remove duplicate lines ##
    with open(log_file, 'r',encoding='utf-8') as log:
        unique_lines = set(log.readlines())
        log.close()

    sorted_lines=sorted(unique_lines)  # sort in alphabetical order
    os.remove(log_file)

    with open(log_file_sorted, 'a',encoding='utf-8') as log_sorted:
        log_sorted.writelines(sorted_lines)
        log_sorted.close()

    return digraph

def remove_literal_from_nodes_old(g,graph,digraph,ontology): ##OLD
    '''remove literal and other expression from the graph in order to keep only the nodes'''

    datatypeproperties=retreive_datatype_properties(ontology)

    for subj, pred, obj in g:
        last_part_pred=get_last_folder_part(pred,'/')

        if (('label' in last_part_pred) or ('type' in last_part_pred) or
           ('inScheme' in last_part_pred) or ('description' in last_part_pred) or
           ('comment' in last_part_pred) or last_part_pred in datatypeproperties):
            pass
        else :
            last_part_subj=get_last_folder_part(subj,'/')
            last_part_obj=get_last_folder_part(obj,'/')
            graph.add_edge(str(last_part_subj),str(last_part_obj),label=str(last_part_pred))
            digraph.add_edge(str(last_part_subj),str(last_part_obj),label=str(last_part_pred))

def log_kpis(file_name,digraph,cumul_nodes,cumul_density):
    '''compute and logs KPIS'''

    logger = logging.getLogger('Graph_KPI')

    logger.info('##################################################')
    logger.info('Knowledge Graph : %s',file_name)
    logger.info('Number of Nodes : %s',digraph.number_of_nodes())
    logger.info('Number of edges : %s',digraph.number_of_edges())
    cumul_nodes = cumul_nodes + digraph.number_of_nodes()
    logger.info('cumulative number of nodes : %s',cumul_nodes )
    logger.info('degree_histogram : %s', degree_histogram(digraph))
    logger.info('number of self loop : %s', number_of_selfloops(digraph))
    logger.info('####  KPIs ####')
    logger.info('DiGraph density : %s',density(digraph))
    cumul_density = cumul_density + density(digraph)
    logger.info('cumulative density : %s',cumul_density)
    logger.info('Average degree connectivity : %s', average_degree_connectivity(digraph))
    logger.info('#### Subject, Object, predicate ####')
    for s, p, data in digraph.edges(data=True):
        logger.info('%s,%s,%s',s,p,data)
    logger.info('#### NODES #### :%s',len(digraph.nodes))
    logger.info('%s',digraph.nodes)
    logger.info('##################################################\n')

    return cumul_nodes, cumul_density
