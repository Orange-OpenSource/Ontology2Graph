# Software Name : Ontologie2Graph
# SPDX-FileCopyrightText: Copyright (c) Orange SA
# SPDX-License-Identifier: BSD-4-Clause
#
# This software is distributed under the BSD 4-Clause "Original" or "Old" License,
# see the "LICENSE" file for more details or <license-url

''' Graph visualization utilities for creating interactive HTML displays.

This module provides two main approaches for visualizing NetworkX graphs as interactive
HTML files using the pyvis library. It offers both basic and advanced visualization
modes with different levels of customization and interactivity.

Functions:
    visu_graph_advanced: Creates sophisticated interactive visualizations with:
        - Node categorization and type-based filtering
        - Dynamic styling and color coding
        - Interactive controls (toggle literals, filter by type, etc.)
        - Enhanced physics simulation
        - Custom JavaScript for advanced interactions
        - Dark theme with responsive design
        
    visu_graph_basic: Creates simple graph visualizations with:
        - Basic pyvis network display
        - Standard physics simulation
        - Dark gray theme
        - Minimal customization
        - Fast rendering for simple use cases

Both functions:
    - Accept NetworkX graph objects as input
    - Generate HTML files with embedded visualizations
    - Automatically open results in the default web browser
    - Support directed graphs with proper edge visualization

The module is designed for visualizing RDF/ontology graphs but can work with any
NetworkX graph structure. Advanced mode is recommended for complex graphs requiring
detailed analysis, while basic mode is suitable for quick previews and simple graphs.

Dependencies:
    - pyvis: For creating interactive network visualizations
    - networkx: Graph data structure (input)
    - webbrowser: For automatically opening HTML results
    - pathlib: For file path handling'''

import webbrowser
import os
from pathlib import Path
from pyvis.network import Network

def visu_graph_advanced(graph,file,html_folder,node_type_lists):
    ''' Create an advanced interactive HTML visualization of a graph with enhanced styling
    and node categorization.
    
    This function generates a sophisticated pyvis network visualization with custom styling,
    node categorization, interactive controls, and filtering capabilities. It creates an HTML
    file with embedded JavaScript for dynamic interaction and automatically opens it in the 
    default web browser.
    
    Args:
        graph (networkx.Graph): NetworkX graph object to visualize
        file (str or Path): Original file path used for naming the output HTML file
        html_folder (str or Path): Directory where the HTML visualization will be saved
        node_type_lists (tuple): Tuple containing 6 sets of node categorizations:
                    (trouble_ticket_nodes,change_request_nodes,application_nodes,
                    network_resource_nodes,network_interface_nodes,network_link_nodes)
    
    Features:
        - Dark theme with responsive design (95vh height, 100% width)
        - Barnes-Hut physics simulation with optimized parameters
        - Color-coded edges: cyan for entity-to-entity, green for entity-to-literal
        - Dynamic node sizing based on degree (connectivity)
        - Node coloring: blue for entities, green for literals
        - Interactive controls:
            * Toggle literal node visibility
            * Show only connected nodes to selected node
            * Filter by node type categories
            * Reset all filters
        - Hover tooltips with node/edge information
        - Navigation buttons and keyboard controls
        - Physics configuration panel
        
    Output:
        - Creates HTML file named after the input file in the specified folder
        - Automatically opens the visualization in the default web browser
        - No return value (void function)
    
    Example:
        >>> node_lists = (tt_nodes, cr_nodes, app_nodes, nr_nodes, ni_nodes, nl_nodes)
        >>> visu_graph_advanced(my_graph, "ontology.ttl", "/output/html", node_lists)
        # Creates /output/html/ontology.html and opens it in browser'''

    trouble_ticket_nodes, change_request_nodes, application_nodes,\
        network_resource_nodes, network_interface_nodes, network_link_nodes = node_type_lists

    ### Create network with responsive sizing ###
    net = Network(height="95vh", width="100%", bgcolor="#1a1a1a",directed=True)
    net.barnes_hut()

    ### Convert NetworkX graph to pyvis first ###
    net.from_nx(graph)

    ### Improved physics settings for better stability and readability ###
    net.set_options(
        """{
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
                "iterations": 20,
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
        }"""
    )

    ### Color code edges: cyan for entity-to-entity, green for entity-to-literal ###
    edge_colors = {
        'entity_to_entity': '#00d4ff',  # Cyan for entity relationships
        'entity_to_literal': '#00cc66'   # Green for literal/datatype properties
    }

    ### Apply colors and styling to edges based on whether they connect to literals or entities ###
    for edge in net.edges:
        edge_label = edge.get('label', '')
        ### Get edge data from original graph to determine type ###
        edge_type = 'entity_to_entity'  # default
        for u, v, data in graph.edges(data=True):
            if (edge.get('from') == u or edge.get('from') == str(u)) and \
               (edge.get('to') == v or edge.get('to') == str(v)):
                edge_type = data.get('edge_type', 'entity_to_entity')
                break

        edge['color'] = edge_colors.get(edge_type, '#888888')
        ### Tooltip shows relationship type and category ###
        edge['title'] = f"{edge_label} ({edge_type.replace('_', ' ')})"

    ### Calculate node sizes based on degree (connectivity) ###
    if len(graph.nodes()) > 0:
        degrees = dict(graph.degree())
        max_degree = max(degrees.values()) if degrees else 1
        min_degree = min(degrees.values()) if degrees else 0
        degree_range = max_degree - min_degree if max_degree > min_degree else 1

        ### Identify literal nodes (nodes that are targets of entity_to_literal edges) ###
        literal_nodes = set()
        for u, v, data in graph.edges(data=True):
            if data.get('edge_type') == 'entity_to_literal':
                literal_nodes.add(v)

        ### Apply node sizes and colors (blue for entities, green for literals) ###
        for node in net.nodes:
            node_id = node['id']
            if node_id in degrees:
                degree = degrees[node_id]
                ### Scale node size between 10 and 40 based on degree ###
                node['size'] = 10 + (30 * (degree - min_degree) / degree_range)

                ### Check if this is a literal node ###
                if node_id in literal_nodes:
                    ### Green color for literal nodes ###
                    node['color'] = {
                        'border': '#ffffff',
                        'background': '#00cc66',
                        'highlight': {
                            'border': '#ffff00',
                            'background': '#00ff88'
                        }
                    }
                else:
                    ### Blue color for entity nodes ###
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

    ### Add custom JavaScript for node selection and filtering ###
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    ete="entity to entity"
    etl="entity to literal"

    ### Insert custom JavaScript before closing body tag ###
    custom_js = f"""
    <script type="text/javascript">
        // Track literal nodes
        var literalNodeIds = [];
        var literalEdgeIds = [];
        var literalsVisible = false; // Hide literals by default
        var visibleNodes = [];  // Track currently visible nodes (for filtered view)
        var isFiltered = false;  // Track if we're in a filtered view
        var selectedNodeId = null;
        var showConnected = true; // For the new button

        // Identify literal nodes and edges from the graph data
        var allEdges = edges.get();
        allEdges.forEach(function(edge) {{
            if (edge.title && edge.title.includes('{etl}')) {{
                literalNodeIds.push(edge.to);
                literalEdgeIds.push(edge.id);
            }}
        }});

        // Hide all literals by default
        window.addEventListener('DOMContentLoaded', function() {{
            literalNodeIds.forEach(function(nodeId) {{
                nodes.update({{id: nodeId, hidden: true}});
            }});
            literalEdgeIds.forEach(function(edgeId) {{
                edges.update({{id: edgeId, hidden: true}});
            }});
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
                    return visibleNodes.indexOf(edge.from) !== -1 ||
                      visibleNodes.indexOf(edge.to) !== -1;
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
            btn.style.backgroundColor = literalsVisible ? 'rgba(204, 0, 0, 0.8)' :
              'rgba(0, 153, 0, 0.8)';
        }}

    // Add toggle literals button on the top left
    var toggleBtn = document.createElement('button');
    toggleBtn.id = 'toggleLiteralsBtn';
    toggleBtn.innerHTML = 'Show Literals'; // Button starts as 'Show Literals'
    toggleBtn.style.position = 'fixed';
    toggleBtn.style.top = '10px';
    toggleBtn.style.right = '10px';
    toggleBtn.style.backgroundColor = 'rgba(204, 0, 0, 0.8)';
    toggleBtn.style.color = 'white';
    toggleBtn.style.padding = '10px 20px';
    toggleBtn.style.border = 'none';
    toggleBtn.style.borderRadius = '5px';
    toggleBtn.style.cursor = 'pointer';
    toggleBtn.style.zIndex = '1001';
    toggleBtn.style.fontFamily = 'Arial';
    toggleBtn.style.fontSize = '14px';
    toggleBtn.style.fontWeight = 'bold';
    toggleBtn.onclick = toggleLiterals;
    document.body.appendChild(toggleBtn);

        // ...existing code for legend, connected nodes, and instructions...
        // Button to show/hide connected nodes (appears on node select)
        var toggleConnectedBtn = document.createElement('button');
        toggleConnectedBtn.id = 'toggleConnectedBtn';
        toggleConnectedBtn.innerHTML = 'Hide Connected Nodes';
        toggleConnectedBtn.style.position = 'fixed';
        toggleConnectedBtn.style.top = '50px';
        toggleConnectedBtn.style.right = '10px';
        toggleConnectedBtn.style.backgroundColor = 'rgba(0,102,204,0.8)';
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
            '<div style="margin: 5px 0;"><span style="display: inline-block; width: 30px; height:\
              3px; background-color: #00d4ff; margin-right: 8px; vertical-align: middle;">\
              </span><span>{ete}</span></div>' +
            '<div style="margin: 5px 0;"><span style="display: inline-block; width: 30px; height:\
              3px; background-color: #00cc66; margin-right: 8px; vertical-align: middle;">\
              </span><span>{etl}</span></div>';\
        document.body.appendChild(legendDiv);

        // ...existing code for connected nodes and instructions...
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
                    if (connectedNodes.indexOf(edge.from) === -1 ||\
                          connectedNodes.indexOf(edge.to) === -1) {{
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

        // Add instructions overlay
        var instructions = document.createElement('div');
        instructions.style.position = 'fixed';
        instructions.style.top = '10px';
        instructions.style.left = '10px';
        instructions.style.backgroundColor = 'rgba(0,0,0,0.8)';
        instructions.style.color = 'white';
        instructions.style.padding = '15px';
        instructions.style.borderRadius = '5px';
        instructions.style.zIndex = '1000';
        instructions.style.fontFamily = 'Arial';
        instructions.style.fontSize = '12px';
        instructions.innerHTML = '<b>Graph Controls:</b><br>\
              • Click on a node: Isolate the node with their connected nodes and literals<br>\
              • When a node is selected, use the hide/show buttons to hide/show its neighbors<br>\
              • Double-click everywhere outside the graph : Show the entire graph<br>';
        document.body.appendChild(instructions);

    </script>
    """

    ### --- Combined Sidebar for all menus --- ###
    combined_sidebar_js = f"""
    <script type=\"text/javascript\">
        var troubleTicketNodes = {trouble_ticket_nodes if trouble_ticket_nodes else []};
        var changeRequestNodes = {change_request_nodes if change_request_nodes else []};
        var applicationNodes = {application_nodes if application_nodes else []};
        var networkResourceNodes = {network_resource_nodes if network_resource_nodes else []};
        var networkInterfaceNodes = {network_interface_nodes if network_interface_nodes else []};
        var networkLinkNodes = {network_link_nodes if network_link_nodes else []};
        var sidebar = document.createElement('div');
        sidebar.id = 'mainSidebar';
        sidebar.style.position = 'fixed';
        sidebar.style.top = '130px';
        sidebar.style.right = '10px';
        sidebar.style.width = '240px';
        sidebar.style.background = 'rgba(30,30,30,0.95)';
        sidebar.style.color = 'white';
        sidebar.style.padding = '15px';
        sidebar.style.borderRadius = '8px';
        sidebar.style.zIndex = '1001';
        sidebar.style.fontFamily = 'Arial';
        sidebar.style.fontSize = '13px';
        sidebar.innerHTML = `
            <b>Trouble Tickets</b><br>
            <select id="ttDropdown" style="width:100%;margin-bottom:5px;">
                <option value="">-- Select Trouble Ticket --</option>
            </select>
            <button id="showAllTTBtn" style="margin-top:5px;width:100%;">Show Only Trouble Tickets</button>
            <button id="resetTTBtn" style="margin-top:5px;width:100%;">Reset Filter</button>
            <hr style="margin:5px 0; border:1px solid #444;">
            <b>Change Requests</b><br>
            <select id="crDropdown" style="width:100%;margin-bottom:5px;">
                <option value="">-- Select Change Request --</option>
            </select>
            <button id="showAllCRBtn" style="margin-top:5px;width:100%;">Show Only Change Requests</button>
            <button id="resetCRBtn" style="margin-top:5px;width:100%;">Reset Filter</button>
            <hr style="margin:5px 0; border:1px solid #444;">
            <b>Applications</b><br>
            <select id="appDropdown" style="width:100%;margin-bottom:5px;">
                <option value="">-- Select Application --</option>
            </select>
            <button id="showAllAppBtn" style="margin-top:5px;width:100%;">Show Only Applications</button>
            <button id="resetAppBtn" style="margin-top:5px;width:100%;">Reset Filter</button>
            <hr style="margin:5px 0; border:1px solid #444;">
            <b>Network Resources</b><br>
            <select id="nrDropdown" style="width:100%;margin-bottom:5px;">
                <option value="">-- Select Network Resource --</option>
            </select>
            <button id="showAllNRBtn" style="margin-top:5px;width:100%;">Show Only Network Resources</button>
            <button id="resetNRBtn" style="margin-top:5px;width:100%;">Reset Filter</button>
            <hr style="margin:5px 0; border:1px solid #444;">
            <b>Network interfaces</b><br>
            <select id="niDropdown" style="width:100%;margin-bottom:5px;">
                <option value="">-- Select Network Interface --</option>
            </select>
            <button id="showAllNIBtn" style="margin-top:5px;width:100%;">Show Only Network Interfaces</button>
            <button id="resetNIBtn" style="margin-top:5px;width:100%;">Reset Filter</button>
            <hr style="margin:5px 0; border:1px solid #444;">
            <b>Network Link</b><br>
            <select id="nlDropdown" style="width:100%;margin-bottom:5px;">
                <option value="">-- Select Network Link --</option>
            </select>
            <button id="showAllNLBtn" style="margin-top:5px;width:100%;">Show Only Network Link</button>
            <button id="resetNLBtn" style="margin-top:5px;width:100%;">Reset Filter</button>
        `;
        document.body.appendChild(sidebar);

        // Trouble Ticket dropdown
        var ttDropdown = document.getElementById('ttDropdown');
        troubleTicketNodes.forEach(function(nodeId) {{
            var option = document.createElement('option');
            option.value = nodeId;
            option.text = nodeId;
            ttDropdown.appendChild(option);
        }});
        ttDropdown.onchange = function() {{
            var selected = this.value;
            if(selected) {{
                network.selectNodes([selected]);
                network.focus(selected, {{scale:1.5, animation:true}});
            }}
        }};
        document.getElementById('showAllTTBtn').onclick = function() {{
            var allNodes = nodes.get({{returnType:"Object"}});
            for (var nodeId in allNodes) {{
                nodes.update({{id: nodeId, hidden: troubleTicketNodes.indexOf(nodeId) === -1}});
            }}
            var allEdges = edges.get({{returnType:"Object"}});
            for (var edgeId in allEdges) {{
                var edge = allEdges[edgeId];
                var show = troubleTicketNodes.indexOf(edge.from) !== -1 &&\
                      troubleTicketNodes.indexOf(edge.to) !== -1;
                edges.update({{id: edgeId, hidden: !show}});
            }}
        }};
        document.getElementById('resetTTBtn').onclick = function() {{
            var allNodes = nodes.get({{returnType:"Object"}});
            for (var nodeId in allNodes) {{
                nodes.update({{id: nodeId, hidden: false}});
            }}
            var allEdges = edges.get({{returnType:"Object"}});
            for (var edgeId in allEdges) {{
                edges.update({{id: edgeId, hidden: false}});
            }}
        }};

        // Change Request dropdown
        var crDropdown = document.getElementById('crDropdown');
        changeRequestNodes.forEach(function(nodeId) {{
            var option = document.createElement('option');
            option.value = nodeId;
            option.text = nodeId;
            crDropdown.appendChild(option);
        }});
        crDropdown.onchange = function() {{
            var selected = this.value;
            if(selected) {{
                network.selectNodes([selected]);
                network.focus(selected, {{scale:1.5, animation:true}});
            }}
        }};
        document.getElementById('showAllCRBtn').onclick = function() {{
            var allNodes = nodes.get({{returnType:"Object"}});
            for (var nodeId in allNodes) {{
                nodes.update({{id: nodeId, hidden: changeRequestNodes.indexOf(nodeId) === -1}});
            }}
            var allEdges = edges.get({{returnType:"Object"}});
            for (var edgeId in allEdges) {{
                var edge = allEdges[edgeId];
                var show = changeRequestNodes.indexOf(edge.from) !== -1 &&\
                    changeRequestNodes.indexOf(edge.to) !== -1;
                edges.update({{id: edgeId, hidden: !show}});
            }}
        }};
        document.getElementById('resetCRBtn').onclick = function() {{
            var allNodes = nodes.get({{returnType:"Object"}});
            for (var nodeId in allNodes) {{
                nodes.update({{id: nodeId, hidden: false}});
            }}
            var allEdges = edges.get({{returnType:"Object"}});
            for (var edgeId in allEdges) {{
                edges.update({{id: edgeId, hidden: false}});
            }}
        }};

        // Application dropdown
        var appDropdown = document.getElementById('appDropdown');
        applicationNodes.forEach(function(nodeId) {{
            var option = document.createElement('option');
            option.value = nodeId;
            option.text = nodeId;
            appDropdown.appendChild(option);
        }});
        appDropdown.onchange = function() {{
            var selected = this.value;
            if(selected) {{
                network.selectNodes([selected]);
                network.focus(selected, {{scale:1.5, animation:true}});
            }}
        }};
        document.getElementById('showAllAppBtn').onclick = function() {{
            var allNodes = nodes.get({{returnType:"Object"}});
            for (var nodeId in allNodes) {{
                nodes.update({{id: nodeId, hidden: applicationNodes.indexOf(nodeId) === -1}});
            }}
            var allEdges = edges.get({{returnType:"Object"}});
            for (var edgeId in allEdges) {{
                var edge = allEdges[edgeId];
                var show = applicationNodes.indexOf(edge.from) !== -1 &&\
                      applicationNodes.indexOf(edge.to) !== -1;
                edges.update({{id: edgeId, hidden: !show}});
            }}
        }};
        document.getElementById('resetAppBtn').onclick = function() {{
            var allNodes = nodes.get({{returnType:"Object"}});
            for (var nodeId in allNodes) {{
                nodes.update({{id: nodeId, hidden: false}});
            }}
            var allEdges = edges.get({{returnType:"Object"}});
            for (var edgeId in allEdges) {{
                edges.update({{id: edgeId, hidden: false}});
            }}
        }};

        // Network Resource dropdown
        var nrDropdown = document.getElementById('nrDropdown');
        networkResourceNodes.forEach(function(nodeId) {{
            var option = document.createElement('option');
            option.value = nodeId;
            option.text = nodeId;
            nrDropdown.appendChild(option);
        }});
        nrDropdown.onchange = function() {{
            var selected = this.value;
            if(selected) {{
                network.selectNodes([selected]);
                network.focus(selected, {{scale:1.5, animation:true}});
            }}
        }};
        document.getElementById('showAllNRBtn').onclick = function() {{
            var allNodes = nodes.get({{returnType:"Object"}});
            for (var nodeId in allNodes) {{
                nodes.update({{id: nodeId, hidden: networkResourceNodes.indexOf(nodeId) === -1}});
            }}
            var allEdges = edges.get({{returnType:"Object"}});
            for (var edgeId in allEdges) {{
                var edge = allEdges[edgeId];
                var show = networkResourceNodes.indexOf(edge.from) !== -1 &&\
                      networkResourceNodes.indexOf(edge.to) !== -1;
                edges.update({{id: edgeId, hidden: !show}});
            }}
        }};
        document.getElementById('resetNRBtn').onclick = function() {{
            var allNodes = nodes.get({{returnType:"Object"}});
            for (var nodeId in allNodes) {{
                nodes.update({{id: nodeId, hidden: false}});
            }}
            var allEdges = edges.get({{returnType:"Object"}});
            for (var edgeId in allEdges) {{
                edges.update({{id: edgeId, hidden: false}});
            }}
        }};

        // Network Interface dropdown
        var niDropdown = document.getElementById('niDropdown');
        networkInterfaceNodes.forEach(function(nodeId) {{
            var option = document.createElement('option');
            option.value = nodeId;
            option.text = nodeId;
            niDropdown.appendChild(option);
        }});
        niDropdown.onchange = function() {{
            var selected = this.value;
            if(selected) {{
                network.selectNodes([selected]);
                network.focus(selected, {{scale:1.5, animation:true}});
            }}
        }};
        document.getElementById('showAllNIBtn').onclick = function() {{
            var allNodes = nodes.get({{returnType:"Object"}});
            for (var nodeId in allNodes) {{
                nodes.update({{id: nodeId, hidden: networkInterfaceNodes.indexOf(nodeId) === -1}});
            }}
            var allEdges = edges.get({{returnType:"Object"}});
            for (var edgeId in allEdges) {{
                var edge = allEdges[edgeId];
                var show = networkInterfaceNodes.indexOf(edge.from) !== -1 &&\
                     networkInterfaceNodes.indexOf(edge.to) !== -1;
                edges.update({{id: edgeId, hidden: !show}});
            }}
        }};
        document.getElementById('resetNIBtn').onclick = function() {{
            var allNodes = nodes.get({{returnType:"Object"}});
            for (var nodeId in allNodes) {{
                nodes.update({{id: nodeId, hidden: false}});
            }}
            var allEdges = edges.get({{returnType:"Object"}});
            for (var edgeId in allEdges) {{
                edges.update({{id: edgeId, hidden: false}});
            }}
        }};

        // Network Link dropdown
        var nlDropdown = document.getElementById('nlDropdown');
        networkLinkNodes.forEach(function(nodeId) {{
            var option = document.createElement('option');
            option.value = nodeId;
            option.text = nodeId;
            nlDropdown.appendChild(option);
        }});
        nlDropdown.onchange = function() {{
            var selected = this.value;
            if(selected) {{
                network.selectNodes([selected]);
                network.focus(selected, {{scale:1.5, animation:true}});
            }}
        }};
        document.getElementById('showAllNLBtn').onclick = function() {{
            var allNodes = nodes.get({{returnType:"Object"}});
            for (var nodeId in allNodes) {{
                nodes.update({{id: nodeId, hidden: networkLinkNodes.indexOf(nodeId) === -1}});
            }}
            var allEdges = edges.get({{returnType:"Object"}});
            for (var edgeId in allEdges) {{
                var edge = allEdges[edgeId];
                var show = networkLinkNodes.indexOf(edge.from) !== -1 &&\
                     networkLinkNodes.indexOf(edge.to) !== -1;
                edges.update({{id: edgeId, hidden: !show}});
            }}
        }};
        document.getElementById('resetNLBtn').onclick = function() {{
            var allNodes = nodes.get({{returnType:"Object"}});
            for (var nodeId in allNodes) {{
                nodes.update({{id: nodeId, hidden: false}});
            }}
            var allEdges = edges.get({{returnType:"Object"}});
            for (var edgeId in allEdges) {{
                edges.update({{id: edgeId, hidden: false}});
            }}
        }};
    </script>
    """

    html_content = html_content.replace('</body>', combined_sidebar_js + custom_js + '</body>')

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    webbrowser.open(html_file,autoraise=True)

def visu_graph_basic(graph,file,html_folder):
    ''' Create a basic interactive HTML visualization of a graph with standard styling.
    
    This function generates a simple pyvis network visualization with basic styling
    and standard physics simulation. It provides a quick and straightforward way to
    visualize graphs without advanced features or customization options.
    
    Args:
        graph (networkx.Graph): NetworkX graph object to visualize
        file (str or Path): Original file path used for naming the output HTML file
        html_folder (str or Path): Directory where the HTML visualization will be saved
    
    Features:
        - Dark gray theme (background color: #222222)
        - Fixed dimensions (1300px height, 100% width)
        - Barnes-Hut physics simulation with standard parameters
        - Red-colored edges with hover effects
        - White font color for node labels
        - No interactive controls or filtering capabilities
        - Fast rendering suitable for simple graphs
    
    Output:
        - Creates an HTML file named after the input file in the specified folder
        - Automatically opens the visualization in the default web browser
        - No return value (void function)
    
    Use Cases:
        - Quick graph previews
        - Simple graph exploration
        - When advanced features are not needed
        - Fast rendering for performance-critical applications
    
    Example:
        >>> visu_graph_basic(my_graph, "network.ttl", "/output/html")
        # Creates /output/html/network.html and opens it in browser'''

    net = Network(height="1300px", width="100%", bgcolor="#222222",directed=True)
    net.barnes_hut()

    net.set_options("""{
        "physics": {
            "solver": "barnesHut",
            "barnesHut": {
                "gravitationalConstant": -80000,
                "centralGravity": 0.3,
                "springLength": 200,
                "springConstant": 0.04,
                "damping": 0.09
                }
            },
        "edges":{
            "color": {
                "color": "#ff0000",
                "highlight": "#ff0000",
                "hover": "#ff0000",
                "inherit": false,
                "opacity": 1.0
                    }
            },
        "nodes": {
            "font": {
                "color": "#ffffff"
            }
        }
        }""")

    net.from_nx(graph)

    os.makedirs(html_folder,exist_ok=True)

    html_file = f'{html_folder}/{Path(file).stem}.html'

    net.save_graph(html_file)

    webbrowser.open(html_file,autoraise=True)
