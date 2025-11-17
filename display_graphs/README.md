# display_graphs


This folder contains utilities and scripts for visualizing and interacting with knowledge graphs previously built.

**Note:** The code in this folder has been enhanced and improved with the assistance of GitHub Copilot (AI assistant) using GPT_4.1, including advanced visualization features, interactive controls, and UI/UX improvements.

## Main Features
- Interactive graph visualization using PyVis and NetworkX
- Customizable node and edge styling (color, size, legend)
- Toggle visibility of literal nodes and edges
- Show/hide nodes connected to a selected node
- Responsive UI with navigation and control buttons

## Key File
- `utils_display.py`: Core utility for rendering and interacting with knowledge graphs. Injects custom JavaScript and CSS for advanced controls.

## Usage
1. Import and use the `visu_graph` function to visualize a NetworkX graph.
2. The generated HTML file will open in your browser with interactive controls:
   - **Hide Literals**: Toggle literal nodes/edges.
   - **Hide Connected Nodes**: When a node is selected, hide/show its directly connected entity nodes (literals remain visible).
   - **Edge Types Legend**: Explains color coding for edges.
   - **Instructions Overlay**: Explains UI controls.

## Requirements
- Python 3.7+
- `pyvis`
- `networkx`
- `rdflib`

Install requirements with:
```bash
pip install pyvis networkx rdflib
```

## Customization
- Edit `utils_display.py` to adjust colors, legend, or UI controls as needed.
- The HTML/JS/CSS is injected dynamically for flexibility.

## Example
```python
from display_graphs.utils.utils_display import visu_graph
# ... build your NetworkX graph ...
visu_graph(graph, 'output_name', 'html_output_folder')
```

## License
This folder is part of the DIGITAL_TWIN/gengraphllm project. See the main project for license details.
