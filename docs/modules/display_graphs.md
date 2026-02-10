# Visualization and Analysis Module

This folder contains utilities and scripts for visualizing and interacting with knowledge graphs previously built.

## Main Components:

- **display_graphs.py**: Main visualization engine supporting multiple rendering modes
- **utils/utils_display.py**: Analytical utilities for graph metrics computation

      -  List of functions :
        - **create_new_log_html_folder**(path)
        - **prepare_graph_to_display**(file, log_html_folder, ontology, mode)
        - **log_kpis**(file_name, digraph, cumul_nodes, cumul_density, mode, node_type_lists=None)
        
- **utils/visu_graph.py**: visualization module for basic or advanced graphs representation

      -  List of functions :
        - **visu_graph_advanced**(graph,file,html_folder,node_type_lists)
        - **visu_graph_basic**(graph,file,html_folder)


## Features
- Interactive HTML generation using web-based visualization libraries
- Key Performance Indicator (KPI) calculation for structural analysis
- Interactive graph visualization using PyVis and NetworkX
- Customizable node and edge styling (color, size, legend)
- Toggle visibility of literal nodes and edges
- Show/hide nodes connected to a selected node
- Responsive UI with navigation and control buttons

## Key File
- **utils_display.py**: Core utility for rendering and interacting with knowledge graphs. Injects custom JavaScript and CSS for advanced controls.

## Usage
The generated HTML file will open in your browser with interactive controls:

   - **Hide or show Literals**
   - **Hide or show Connected Nodes**: When a node is selected, hide/show its directly connected entity nodes (literals remain visible).
   - **Edge Types Legend**: Explains color coding for edges.
   - **Instructions Overlay**: Explains UI controls.

## Logging
Two differents log files track different aspects

   - **URI and Literals :** List of subject, and literals for each graphs 
   - **KPIs Log :** Number of nodes, degree, density ... by graphs

## Customization
- Edit **utils_display.py**, from **utils** folder, to adjust colors, legend, or UI controls as needed.
- The HTML/JS/CSS is injected dynamically for flexibility.

