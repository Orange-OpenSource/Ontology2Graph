# generate_ttl_files

This folder contains scripts and utilities for generating synthetic knowledge graphs in Turtle (.ttl) format based on ontology schemas and prompts.

## Main Components
- **generate_ttl.py**: Main script to generate one or more Turtle files using a large language model(LLM) and a given ontology. Run this script from the `generate_ttl_files` directory.
- **utils_gen/utils.py**: Utility functions for querying the LLM, storing results, checking Turtle syntax, and managing files/folders.

## Features
- Automated generation of Turtle files using LLM, prompt and ontology.
- Configurable number of graphs to generate via the `--nbrttl` command-line argument.
- Logging of generation process and LLM usage statistics (log files are created dynamically in the results folder).
- Automatic folder and file management for results, logs, and temporary files (folders are created as needed).
- Syntax validation for generated Turtle files.
- Support for removing old files before new generation.

## Usage
1. Set your LLM API key in an environment variable called `LLM_PROXY_KEY`.
2. Place your ontology in the appropriate folders (default: `utils_gen/ontologies/`).
3. Modify `utils_gen/prompts/prompts.json` with your own prompt and set `PROMPT_TYPE` in 
generate_ttl.py accordingly?
4. Modify `utils_gen/prompts/models.json` with the model name you want to use with your API.
5. Choose your system prompt in `query_llm` if allowed by your API.
6. Run the script from the `generate_ttl_files` directory:
   ```bash
   python generate_ttl.py --nbrttl <number_of_ttl_files_to_generate>
   ```
7. Generated Turtle files will be stored in a dynamically created `results/synthetics_graphs/<date>/<model>/` folder (created automatically).
8. Log files will be created in the corresponding `logs/` subfolder.

## Requirements
- Python 3.7+
- Required packages: `requests`, `rdflib`, `openai` (and possibly others). Install them manually:
   ```bash
   pip install requests rdflib openai
   ```
   *(No requirements.txt is provided in this folder.)*

## Notes
- Edit `generate_ttl.py` to set the model number (`model_nbr` variable) and other configuration as needed.
- The script sleeps 60 seconds between generations to reset LLM context.
- Make sure to run the script from the `generate_ttl_files` directory for correct path resolution.
- The script and utilities are licensed under BSD-4-Clause.

## License

BSD-4-Clause License - Copyright (c) Orange SA

See the main LICENSE file for complete license terms.
