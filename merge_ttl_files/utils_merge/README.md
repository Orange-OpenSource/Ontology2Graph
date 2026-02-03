# Utils Merge Module

This module provides utility functions for merging multiple Turtle (TTL) knowledge graphs into unified graphs while handling node homonyms and RDF prefixes.

## Overview

The utils_merge module is part of the Ontologie2Graph project and provides the core functionality for:
- Merging multiple TTL files containing RDF knowledge graphs
- Managing RDF prefix declarations across merged files
- Identifying and handling homonymous nodes across graphs
- Creating graphs with different densities by controlling homonym occurrences
- Validating merged TTL files for correct Turtle syntax

## Main Features

### 1. Graph Merging
- Combines multiple individual TTL files into unified knowledge graphs
- Preserves RDF semantics during the merge process
- Handles large-scale graph combinations efficiently

### 2. Homonym Detection and Management
- Identifies nodes that appear with the same name across different graphs
- Counts occurrences of homonymous nodes across the dataset
- Renames homonyms with occurrence indices to ensure uniqueness
- Enables creation of graphs with varying densities by controlling homonym frequency

### 3. Prefix Management
- Extracts and deduplicates RDF prefix declarations
- Removes conflicting prefixes from merged files
- Ensures valid Turtle syntax in output files

### 4. File Organization
- Creates structured directory hierarchies for processed files
- Separates invalid files from successful merges
- Maintains detailed logs of all processing steps

## Key Functions

### `build_merged_folder_paths_and_files(path_files)`
Creates the necessary directory structure and returns file paths for the merging process.

**Returns:**
- `bad_path_result`: Directory for invalid TTL files
- `log_file`: Main processing log file
- `log_file_homonymes`: Homonym processing log
- `log_file_check_ttl`: TTL validation log
- `path_merged`: Directory for merged output files
- `path_homonyme_treated`: Directory for homonym-processed files

### `manage_prefix(path_merged)`
Removes duplicate and conflicting RDF prefix declarations from merged TTL files.

### `find_homonymes_nodes(path_files, logger, ontology)`
Identifies homonymous nodes across multiple TTL files and counts their occurrences.

### `rename_and_merge(path_files, homonymes_nodes_and_occurence, logger, ontology, path_merged)`
Renames homonymous nodes with occurrence indices and merges the files.

### `merge_graph(path_files, path_merged, logger, ontology)`
Main function that merges all valid TTL files in a directory into a single graph.

## Directory Structure After Processing

```
path_files/
├── merged/                                    # Merged TTL files
│   └── homonymes_treated/                     # Files with renamed homonyms
├── Invalid_Turtle_Syntax_for_merged_graphs/   # Invalid TTL files
└── logs/                                      # Processing logs
    ├── merge_graph_YYYY-MM-DD_HH-MM-SS.log
    ├── homonymes_graph_YYYY-MM-DD_HH-MM-SS.log
    └── check_merged_ttl_graph_YYYY-MM-DD_HH-MM-SS.log
```

## Dependencies

- **pathlib**: Cross-platform file path handling
- **collections.Counter**: Node occurrence counting
- **rdflib**: RDF/Turtle format processing (URIRef, Namespace, BNode)
- **networkx**: Graph analysis and manipulation
- **utils_common**: Common utilities for the project

## Logging

The module generates detailed logs for:
- **Merge operations**: File combination and validation results
- **Homonym processing**: Detection and renaming of duplicate nodes
- **TTL validation**: Syntax checking of merged files

All logs include timestamps and detailed error information for debugging and audit purposes.

## Error Handling

- Invalid TTL files are automatically separated into a dedicated directory
- Syntax errors are logged with specific line information
- Processing continues even when individual files fail validation

## Performance Considerations

- Large graph merges are processed efficiently using streaming techniques
- Memory usage is optimized for handling substantial TTL datasets
- Progress is logged for long-running operations

## License

This software is distributed under the BSD 4-Clause "Original" or "Old" License.
Copyright (c) Orange SA