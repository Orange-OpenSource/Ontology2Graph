# GraphGPT-pyth2

This python script is dedicated to query LLM models throught the internal Orange portal [LLM PROXY Portail](https://portal.llmproxy.ai.orange/) in order to generate a knowledge graph in  turtle format based on an ontology schema also in turtle format. Three differents prommpts have been created

    * The First one gives the schema and provides some explanantions.
    * The Second one gives the schema and an extract of a knowledge graph, and provides some explanantions.
    * The Third one gives the schema and a complete knowledge graph, and provides some explanantions.

## Getting started

### Prerequisite

1. You need first to create an account in [LLM PROXY Portail](https://portal.llmproxy.ai.orange/).
2. Then once it is done you must setup a local environment variable called ORANGE_LLM_PROXY_KEY with the value of your LLM_PROXY key.
3. Your turtle files must be placed in the same folder than the python script .

### Start conversion

To launch the python script just type 'python3 graphllm.py'.

Results are displayed on the screen and recorded in a file called 'response.txt' located in the same folder than the python script.

