# Display Graphs Utils

This folder contains utility modules for graph visualization and display functionality used by the display_graphs module.

## Files Overview

### `utils_display.py`
Core utilities for displaying and visualizing RDF/ontology graphs with comprehensive functionality:

**Main Features:**
- Graph preparation and preprocessing for visualization
- HTML folder creation and management  
- Interactive network visualization with pyvis
- Node categorization by type (TroubleTicket, ChangeRequest, Application, etc.)
- KPI calculation and logging (node count, density, degree distribution)
- Graph filtering and cleanup (literal removal, predicate/object filtering)
- Ontology object extraction and analysis

**Key Functions:**
- `create_new_log_html_folder()`: Creates clean log/HTML output directories
- `prepare_graph_to_display_advanced/basic()`: Prepares graphs for visualization modes
- `log_kpis_advanced/basic()`: Logs graph metrics and key performance indicators

### `visu_graph.py`
Graph visualization utilities for creating interactive HTML displays with two main approaches:

**Advanced Visualization (`visu_graph_advanced`):**
- Node categorization and type-based filtering
- Dynamic styling and color coding
- Interactive controls (toggle literals, filter by type, etc.)
- Enhanced physics simulation
- Custom JavaScript for advanced interactions
- Dark theme with responsive design

**Basic Visualization (`visu_graph_basic`):**
- Standard pyvis network display
- Basic physics simulation
- Dark gray theme
- Minimal customization
- Fast rendering for simple use cases

## Output

Both visualization modes generate interactive HTML files that can be opened in any modern web browser, featuring:
- Zoomable and pannable network views
- Node selection and highlighting
- Interactive controls for filtering and display options
- Responsive design for different screen sizes

## License

BSD-4-Clause License - Copyright (c) Orange SA

See the main LICENSE file for complete license terms.