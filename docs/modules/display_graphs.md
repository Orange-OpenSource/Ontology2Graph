# Visualization and Analysis Module

This folder contains utilities and scripts for visualizing and interacting with knowledge graphs previously built.

**Key Components:**
- `display_graphs.py`: Main visualization engine supporting multiple rendering modes
- `utils/utils_display.py`: Analytical utilities for graph metrics computation
- Interactive HTML generation using web-based visualization libraries
- Key Performance Indicator (KPI) calculation for structural analysis
- `utils/visu_graph.py`: visualization module for basic or advanced graphs representation

## Main Features
- Interactive graph visualization using PyVis and NetworkX
- Customizable node and edge styling (color, size, legend)
- Toggle visibility of literal nodes and edges
- Show/hide nodes connected to a selected node
- Responsive UI with navigation and control buttons

## Key File
- `utils_display.py`: Core utility for rendering and interacting with knowledge graphs. Injects custom JavaScript and CSS for advanced controls.

## Usage
The generated HTML file will open in your browser with interactive controls:

   - **Hide Literals**: Toggle literal nodes/edges.
   - **Hide Connected Nodes**: When a node is selected, hide/show its directly connected entity nodes (literals remain visible).
   - **Edge Types Legend**: Explains color coding for edges.
   - **Instructions Overlay**: Explains UI controls.

## Customization
- Edit `utils_display.py`, from `utils` folder, to adjust colors, legend, or UI controls as needed.
- The HTML/JS/CSS is injected dynamically for flexibility.

## License

BSD-4-Clause License - Copyright (c) Orange SA

See the main LICENSE file for complete license terms.
