'''list of function to be used '''

import logging
import webbrowser
import os
import shutil
from pathlib import Path
from rdflib import URIRef, Literal, Namespace,BNode
from pyvis.network import Network
import networkx as nx
from networkx.classes.function import density, degree_histogram, number_of_selfloops
from networkx import average_degree_connectivity
import rdflib
from utils_common import utils as utils_common

def create_new_log_html_folder(path):
    '''create new log_html folder'''
    if Path(path).is_file():
        log_html_folder = Path(f'{str(Path(path).parent)}/log_html/')
    else:
        log_html_folder = Path(f'{str(Path(path))}/log_html/')

    if log_html_folder.exists() and log_html_folder.is_dir():
        shutil.rmtree(log_html_folder)

    Path.mkdir(log_html_folder)

    return log_html_folder

def visu_graph_advanced(graph,file,html_folder,node_type_lists):
    '''display the graph with enhanced visualization settings'''

    trouble_ticket_nodes, change_request_nodes, application_nodes,\
        network_resource_nodes, network_interface_nodes, network_link_nodes = node_type_lists

    # Create network with responsive sizing
    net = Network(height="95vh", width="100%", bgcolor="#1a1a1a",directed=True)
    net.barnes_hut()

    # Convert NetworkX graph to pyvis first
    net.from_nx(graph)

    # Improved physics settings for better stability and readability
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

    ete="entity to entity"
    etl="entity to literal"

    # Insert custom JavaScript before closing body tag
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

    # --- Combined Sidebar for all menus ---
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
    '''dysplay the graph'''

    net = Network(height="1300px", width="100%", bgcolor="#222222",directed=True)
    net.barnes_hut()
    #net.repulsion()

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

    #net.set_options(options)
    net.from_nx(graph)
    #net.show_buttons(filter_=['physics'])

    #for edges in net.edges:
    #    edges["color"]="green"

    os.makedirs(html_folder,exist_ok=True)

    html_file = f'{html_folder}/{Path(file).stem}.html'

    net.save_graph(html_file)

    #webbrowser.open(f'file://///wsl.localhost/Ubuntu-24.04{html_file}',autoraise=True)
    webbrowser.open(html_file,autoraise=True)

def prepare_graph_to_display_advanced(file, log_html_folder, ontology):
    '''set the graph and remove literal and other expression from the graph in order to keep only
    the real nodes and their relation to display, log some inforations'''

    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    skos = Namespace("http://www.w3.org/2004/02/skos/core#")
    #noria = Namespace("http://www.semanticweb.org/noria#")

    trouble_ticket_nodes = set()
    change_request_nodes = set()
    application_nodes = set()
    network_resource_nodes = set()
    network_interface_nodes = set()
    network_link_nodes = set()

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

    dtp = utils_common.retreive_onto_object(ontology,"DatatypeProperty")
    print('Datatype Properties:',dtp)

    ### populate graph with nodes and relations (including literals) ###
    for subj, pred, obj in g:

        #subj=str(subject)
        #obj=str(object)
       # pred=str(predicate)

        short_pred=Path(str(pred)).name
        if '#' in short_pred:
            short_pred=short_pred.split('#',1)[1]
        short_subj=Path(str(subj)).name

        # Retrieve nodes by their type to be used in the UI menu for filtering
        if short_pred == "type":
            if Path(str(obj)).name == "TroubleTicket": # Identify TroubleTicket nodes
                trouble_ticket_nodes.add(str(short_subj))

            if Path(str(obj)).name == "ChangeRequest": # Identify ChangeRequest nodes
                change_request_nodes.add(str(short_subj))

            if Path(str(obj)).name == "Application": # Identify Application nodes
                application_nodes.add(str(short_subj))

            if Path(str(obj)).name == "Resource": # Identify NetworkResource nodes
                network_resource_nodes.add(str(short_subj))

            if Path(str(obj)).name == "NetworkInterface": # Identify NetworkInterface nodes
                network_interface_nodes.add(str(short_subj))

            if Path(str(obj)).name == "NetworkLink": # Identify NetworkLink nodes
                network_link_nodes.add(str(short_subj))

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
                short_subjbn = Path(str(subjbn)).name
                short_predbn = Path(str(predbn)).name
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

    node_type_lists = [list(trouble_ticket_nodes), list(change_request_nodes),\
                        list(application_nodes), list(network_resource_nodes),\
                            list(network_interface_nodes), list(network_link_nodes)]
    return digraph, node_type_lists

def prepare_graph_to_display_basic(file,log_html_folder,ontology):
    '''set the graph and remove literal and other expression from the graph in order to keep only
    the real nodes and their relation to display, log some inforations'''

    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    skos = Namespace("http://www.w3.org/2004/02/skos/core#")

    ### set logger ###
    log_file=f'{Path(log_html_folder)}/URI_and_LITERAL.log'
    log_file_sorted=f'{Path(log_html_folder)}/URI_and_LITERAL_sorted.log'

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

    ### populate graph with nodes and relations only ###
    for subj, pred, obj in g:

        short_pred=Path(str(pred)).name
        short_subj=Path(str(subj)).name
        short_obj=Path(str(obj)).name
        #dtp = utils_common.retreive_datatype_properties(ontology)
        dtp = utils_common.retreive_onto_object(ontology,"DatatypeProperty")

        if (isinstance(subj, URIRef) and isinstance(obj, URIRef) and (pred != rdf.type) and\
            (pred != skos.inScheme) and (pred != rdfs.isDefinedBy) and\
                (short_pred not in dtp)):
            digraph.add_edge(str(short_subj), str(short_obj), label=str(short_pred),color='white')
            logger_file1.info('URIRef Subject : %s',subj)

        if isinstance(obj, Literal):
            logger_file1.info('Literal Object : %s',obj)

        if isinstance(subj, BNode) and (pred != rdf.type) and (pred != skos.inScheme):
            logger_file1.info('Blank Node Subject :%s',subj)
            for subjbn, predbn in g.subject_predicates(subj):
                short_subjbn=Path(str(subjbn)).name
                short_predbn=Path(str(predbn)).name
                digraph.add_edge(short_subjbn,short_obj,label=short_predbn,\
                    color='white')
                logger_file1.info('Blank Node Subject :%s,Predicate :%s,Object : %s',short_subjbn,\
                    short_predbn,short_obj)

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

def log_kpis_advanced(file_name,digraph,cumul_nodes,cumul_density,node_type_lists):
    '''compute and logs KPIS'''
    trouble_ticket_nodes, change_request_nodes, application_nodes,\
          network_resource_nodes, network_interface_nodes, network_link_nodes = node_type_lists

    logger = logging.getLogger('graph_kpi')

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
    logger.info('trouble tickets nodes :%s',trouble_ticket_nodes)
    logger.info('change request nodes :%s',change_request_nodes)
    logger.info('application nodes :%s',application_nodes)
    logger.info('network resource nodes :%s',network_resource_nodes)
    logger.info('network interface nodes :%s',network_interface_nodes)
    logger.info('network link nodes :%s',network_link_nodes)
    logger.info('##################################################\n')

    return cumul_nodes, cumul_density

def log_kpis_basic(file_name,digraph,cumul_nodes,cumul_density):
    '''compute and logs KPIS'''

    logger = logging.getLogger('graph_kpi')

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

### old code below for reference ###

def remove_literal_from_nodes_old(g,graph,digraph,ontology): 
    '''remove literal and other expression from the graph in order to keep only the nodes

    datatypeproperties=utils_common.retreive_onto_object(ontology,"DatatypeProperty")

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
            digraph.add_edge(str(last_part_subj),str(last_part_obj),label=str(last_part_pred))'''

def remove_pred_obj(expr, graph, predi, obje):
    '''remove predicate and target object of an edge
    edges_to_remove = [(u, v) for u, v, attr in graph.edges(data=True)
                         if attr.get(expr) == predi and v == obje]
    return graph.remove_edges_from(edges_to_remove)'''
    
def get_last_folder_part(string, sep_char):
    """get last part of a folder string
    string_parts=string.split(sep_char)
    last_part=string_parts[len(string_parts)-1]
    if last_part=='':
        last_part=string_parts[len(string_parts)-2]
    return last_part"""
    
def retreive_onto_object(ontology,object_type):
    
    '''create a list of all the object declares in the ontology
    object_type can be DatatypeProperty, ObjectProperty or Class

    index_list=[]
    objects=[]
    object_clean=[]

    #build index list of Object
    with open(f'{ontology}', 'r',encoding='utf-8') as file:
        for index, line in enumerate(file, start=1):
            if f":{object_type} " in line :
                index_list.append(index-1)
    file.close()

    #retrieve Object based on index list
    with open(f'{ontology}', 'r',encoding='utf-8') as file:
        for index, line in enumerate(file, start=1):
            if index in index_list:
                objects.append(line.strip())
                #print(line.strip())
    file.close()

    #clean Object
    for obj in objects:
        obj=obj.replace('noria:',"")
        object_clean.append(obj)
    #print(dtproperties)
    return object_clean'''