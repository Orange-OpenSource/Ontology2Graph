# generate_ttl_files

This folder contains scripts and utilities for generating synthetic knowledge graphs in Turtle (.ttl) format based on ontology schemas and prompts.

## Main Components
- **generate_ttl.py**: Main script to generate one or more Turtle files using a language model and a given ontology.
- **utils_gen/utils.py**: Utility functions for querying the LLM, storing results, checking Turtle syntax, and managing files/folders.

## Features
- Automated generation of Turtle files using LLM prompts and ontology.
- Configurable number of graphs to generate via command-line argument.
- Logging of generation process and LLM usage statistics.
- Automatic folder and file management for results, logs, and temporary files.
- Syntax validation for generated Turtle files.
- Support for removing old files before new generation.

## Usage
1. Set your LLM API key in the environment variable `LLM_PROXY_KEY`.
2. Place your ontology and prompt files in the appropriate folders.
3. Run the script from the `generate_ttl_files` directory:
   ```bash
   python generate_ttl.py <number_of_ttl_files_to_generate>
   ```
4. Generated Turtle files will be stored in the `results/synthetics_graphs` folder.
5. Logs will be created in the specified log folder.

## Requirements
- Python 3.7+
- Required packages listed in `requirements.txt` (e.g., requests, rdflib, etc.)

Install requirements with:
```bash
pip install -r requirements.txt
```

## Notes
- Edit `generate_ttl.py` to set the model number (model_nbr variable) and other configuration as needed.
- The script sleeps 60 seconds between generations to reset LLM context.
- Make sure to run the script from the `generate_ttl_files` directory for correct path resolution.

## License
This folder is part of the DIGITAL_TWIN/gengraphllm project. See the main project for license details.
