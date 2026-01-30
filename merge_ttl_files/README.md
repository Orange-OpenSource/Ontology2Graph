# TTL Files Merger

This module provides functionality for merging multiple TTL (Turtle) knowledge graphs into unified, consolidated graphs while handling duplicate nodes and maintaining RDF integrity.

## Overview

The TTL merger processes sets of synthetic knowledge graphs in turtle format based on the merging by exact matching method. It identifies overlapping entities (homonymes), and creates different merged graphs with different density based on a sequential homonymes nodes renaming.

## Features

- **Duplicate Node Detection**: Automatically identifies homonymous nodes across multiple TTL files
- **Intelligent Merging**: Combines graphs while preserving semantic relationships
- **Prefix Management**: Handles RDF namespace prefixes during the merge process
- **Validation**: Verifies TTL syntax validity of merged outputs
- **Flexible Node Density**: Supports different graph densities based on homonym occurrence thresholds
- **Comprehensive Logging**: Detailed logging for merge operations, homonym detection, and validation

## Directory Structure

```
merge_ttl_files/
├── merge_ttl.py           # Main script for merging TTL files
├── utils_merge/           # Utility functions for merging operations
│   ├── __init__.py       
│   └── utils.py          # Core merging utilities
├── lib/                  # External libraries (if any)
└── README.md             # This file
```

## Usage

### Basic Usage

```bash
python merge_ttl.py --path_file <graphs_folder> --ontology <ontology_file>
```

### Arguments

- `--path_file`: Absolute path to the folder containing synthetic knowledge graphs to merge
- `--ontology`: Path to the ontology TTL file used as schema reference

## Process Workflow

1. **Path Setup**: Creates necessary output directories for merged files and logs
2. **Homonym Detection**: Scans all TTL files to identify duplicate node names
3. **Occurrence Counting**: Counts how many files contain each homonymous node
4. **Merge Strategy**: Applies renaming strategy based on occurrence thresholds
5. **File Merging**: Combines processed TTL files into unified graphs
6. **Prefix Management**: Cleans up RDF namespace prefixes
7. **Validation**: Validates merged TTL syntax and moves invalid files

## Output Structure

The merger creates the following output structure:
```
results/merged_graphs/
├── merged/                    # Successfully merged TTL files
├── Invalid_Turtle_Syntax/     # Files with syntax errors
├── duplicate_treated/         # Intermediate files with renamed duplicates
└── logs/                      # Process logs
    ├── merge_log_[timestamp].log
    ├── homonymes_log_[timestamp].log
    └── check_merged_ttl_log_[timestamp].log
```

## Key Functions

### Core Utilities (`utils_merge/utils.py`)

- `build_merged_folder_paths_and_files()`: Sets up directory structure
- `find_homonymes_nodes()`: Identifies duplicate nodes across files
- `rename_and_merge()`: Processes homonyms and merges files
- `manage_prefix()`: Cleans RDF namespace prefixes
- `merge_graph()`: Combines multiple TTL files into one

## Dependencies

- **Python 3.8+**
- **rdflib**: RDF processing and Turtle format handling
- **networkx**: Graph processing capabilities
- **pathlib**: Cross-platform file path operations
- **utils_common**: Shared utilities from parent project

## Error Handling

- **Syntax Errors**: Invalid TTL files are moved to `Invalid_Turtle_Syntax/`
- **Missing Files**: Graceful handling of missing input files
- **Memory Management**: Efficient processing for large graph sets
- **Timeout Protection**: Prevents hanging on problematic files

## Integration

This module integrates with the broader Ontologie2Graph ecosystem:
- Uses shared utilities from `utils_common/`
- Processes outputs from `generate_ttl_files/`

## Logging

Three separate log files track different aspects:
- **Merge Log**: Overall merge process and statistics
- **Homonyms Log**: Duplicate node detection details
- **Validation Log**: TTL syntax checking results

## Performance Considerations

- Processes files in batches to manage memory usage
- Uses efficient RDF parsing libraries
- Implements smart caching for repeated operations
- Optimized for handling large numbers of synthetic graphs

## License

BSD-4-Clause License - Copyright (c) Orange SA

See the main LICENSE file for complete license terms.