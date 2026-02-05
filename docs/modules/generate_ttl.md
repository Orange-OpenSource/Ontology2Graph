# generate_ttl_files

This folder contains scripts and utilities for generating synthetic knowledge graphs in Turtle (.ttl) format based on ontology schemas and prompts.

## Main Components
- **generate_ttl.py**: Main script to generate one or more Turtle files using a large language model(LLM) and a given ontology. Run this script from the `generate_ttl_files` directory.
- **utils_gen/utils.py**: Utility functions for querying the LLM, storing results, checking Turtle syntax, and managing files/folders.

**Key Components:**
- `generate_ttl.py`: Primary generation engine implementing LLM-based graph synthesis
- `utils_gen/utils.py`: Supporting utilities for model configuration, prompt management and graph validation
- Multi-model support architecture with configurable prompt strategies
- Integrated TTL syntax validation & turtle formating pipeline

## Features
- Automated generation of Turtle files using LLM, prompt and ontology.
- Configurable number of graphs to generate via the `--nbrttl` command-line argument.
- The `--reasoner` argument specifies which ontology reasoner to use for consistency checking of the generated Turtle files. Valid values are `Pellet` or `HermiT` (case-sensitive). The reasoner will be used to check for logical inconsistencies in the generated graphs. If not set correctly, the script will raise an error.
- Logging of generation process and LLM usage statistics (log files are created dynamically in the results folder).
- Automatic folder and file management for results, logs, and temporary files (folders are created as needed).
- Syntax validation for generated Turtle files.
- Support for removing old files before new generation.

Each TTL file generated is automatically checking by [Ontology engineering tool](https://github.com/atextor/owl-cli) for Turtle format rearrangement and [Turtle Validator](https://github.com/IDLabResearch/TurtleValidator) for syntax validation. Validated files are stored in the `results/synthetic_graphs/` directory in TTL format.

## License

BSD-4-Clause License - Copyright (c) Orange SA

See the main LICENSE file for complete license terms.
