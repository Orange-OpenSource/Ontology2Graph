# Utils Generation Module

This module provides core utility functions for knowledge graph generation using Large Language Models (LLMs). It handles the complete pipeline from LLM querying to graph validation and quality assurance.

## Overview

The `utils.py` module contains essential functions for:
- LLM API interaction and query management
- Graph generation result processing and storage
- TTL format validation and formatting
- Ontological consistency checking with formal reasoners
- File and directory management for the generation pipeline

## Functions

### Core Generation Functions

#### `query_llm(ontology_file, prompt_file, model, prompt_type)`
Sends prompts and ontology schemas to LLM APIs for knowledge graph generation.

**Purpose:** Interfaces with OpenAI-compatible APIs to generate synthetic knowledge graphs
**Parameters:**
- `ontology_file`: Path to ontology schema file
- `prompt_file`: Path to generation prompt template
- `model`: Target LLM model identifier
- `prompt_type`: Generation strategy type

**Returns:** LLM response containing generated graph data

#### `storing_results(response, temp_file, file_result, logger, model)`
Processes and stores LLM-generated graph content with validation.

**Purpose:** Extracts TTL content from LLM responses and saves to designated files
**Parameters:**
- `response`: LLM response object
- `temp_file`: Temporary file path for processing
- `file_result`: Final output file path
- `logger`: Logging instance
- `model`: Model identifier for tracking

**Features:**
- Automatic TTL content extraction
- Token usage tracking
- Error handling and logging

### Configuration and Setup Functions

#### `model_to_choose(model_nbr)`
Selects LLM model based on configuration number.

**Purpose:** Maps model numbers to actual LLM identifiers
**Parameters:**
- `model_nbr`: Numeric model selector

**Returns:** String identifier for the selected LLM model
**Configuration:** Uses `models/models.json` for model mapping

#### `build_folder_paths_and_files(model)`
Constructs organized directory structure for graph generation outputs.

**Purpose:** Creates timestamped folders and file paths for organized storage
**Parameters:**
- `model`: LLM model identifier

**Returns:** Dictionary containing all necessary file and folder paths
**Structure Created:**
```
results/synthetic_graphs/YYYY-MM-DD/
├── generated_graphs/
├── not_formatted/
└── invalid_reasoner/
```

### Quality Assurance Functions

#### `check_graph_format(folder_path, notformated_path, logger)`
Validates and formats TTL files using external formatting tools.

**Purpose:** Ensures TTL files conform to proper formatting standards
**Parameters:**
- `folder_path`: Directory containing TTL files to check
- `notformated_path`: Directory for improperly formatted files
- `logger`: Logging instance

**Process:**
1. Applies OWL-CLI formatting tool to each TTL file
2. Validates formatting compliance
3. Quarantines non-conformant files
4. Logs formatting results

#### `check_graph_reasoner(folder_path, invalid_reasoner_path, ontology, reasoner, logger)`
Validates knowledge graphs for ontological consistency using formal reasoning engines.

**Purpose:** Performs comprehensive ontological consistency checking
**Parameters:**
- `folder_path`: Directory containing TTL graph files to validate
- `invalid_reasoner_path`: Directory for quarantining invalid graphs
- `ontology`: Path to ontology TTL file for consistency checking
- `reasoner`: Reasoning engine ("HermiT" or "Pellet")
- `logger`: Logging instance

**Validation Process:**
1. Concatenates each graph with the ontology
2. Converts to OWL/XML format for reasoning compatibility
3. Applies formal reasoner to detect logical inconsistencies
4. Identifies unsatisfiable classes (equivalent to owl:Nothing)
5. Quarantines invalid graphs with INVALID_ prefix

**Supported Reasoners:**
- **HermiT**: High-performance tableau-based reasoner
- **Pellet**: OWL DL reasoning engine

**Error Detection:**
- Ontological inconsistency errors
- Unsatisfiable class detection
- Resource overflow handling

### Utility Functions

#### `remove_file_in_folder(folder_path)`
Removes all files from a specified directory.

**Purpose:** Cleanup utility for folder management
**Parameters:**
- `folder_path`: Directory to clear

## Configuration Files

The module relies on several configuration files located in subdirectories:

### `models/models.json`
Maps numeric identifiers to LLM model names.
```json
{
  "1": "gpt-4",
  "2": "claude-3",
  "3": "gemini-pro"
}
```

### `prompts/prompts.json`
Defines generation strategies and prompt templates.
```json
{
  "1": "basic_generation",
  "2": "example_guided",
  "3": "complete_reference"
}
```

### `ontologies/`
Directory containing ontology schema files in TTL format.

## Dependencies

### Required Python Packages
- `openai`: LLM API integration
- `rdflib`: RDF graph processing
- `owlready2`: Ontology reasoning and validation
- `pathlib`: Cross-platform file operations
- `json`: Configuration file parsing

### External Tools
- **OWL-CLI**: TTL formatting and validation tool
- **Turtle Validator**: Syntax validation utility
- **HermiT/Pellet**: Formal reasoning engines (via owlready2)

## Usage Example

```python
from utils_gen import utils

# Configure model and paths
model = utils.model_to_choose("1")  # Select GPT-4
paths = utils.build_folder_paths_and_files(model)

# Generate knowledge graph
response = utils.query_llm(
    ontology_file="./ontologies/schema.ttl",
    prompt_file="./prompts/basic.txt", 
    model=model,
    prompt_type="1"
)

# Store and validate results
utils.storing_results(response, paths['temp'], paths['output'], logger, model)
utils.check_graph_format(paths['generated'], paths['invalid_format'], logger)
utils.check_graph_reasoner(
    folder_path=paths['generated'],
    invalid_reasoner_path=paths['invalid_reasoner'], 
    ontology="./ontologies/schema.ttl",
    reasoner="HermiT",
    logger=logger
)
```

## Error Handling

The module implements comprehensive error handling for:
- LLM API failures and timeouts
- Invalid TTL syntax and formatting issues
- Ontological consistency violations
- File I/O operations and permissions
- Resource limitations during reasoning

## Logging

All functions support detailed logging with configurable verbosity levels:
- Generation progress and token usage
- Validation results and error details
- File operations and quarantine actions
- Performance metrics and timing information

## Integration

This module integrates seamlessly with:
- Main generation script (`generate_ttl.py`)
- Common utilities (`utils_common/`)
- Visualization module (`display_graphs/`)
- Merging module (`merge_ttl_files/`)

---

**Last Updated:** January 29, 2026  
**Version:** 2.0 (Added reasoning validation)