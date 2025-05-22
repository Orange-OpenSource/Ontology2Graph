# GraphGPT-pyth2

This python script is dedicated to query LLM models throught the internal Orange portal [LLM PROXY Portail](https://portal.llmproxy.ai.orange/) in order to generate a knowledge graph in  turtle format based on the ontologies schema also in turtle format

## Getting started

### Prerequisite

1. You need first to create an account in [LLM PROXY Portail](https://portal.llmproxy.ai.orange/).
2. Then once it is done you must setup a local environment variable called ORANGE_LLM_PROXY_KEY with the value of your LLM_PROXY key.
3. Your turtle files must be placed in the same folder than the python script .

### Start conversion

To launch the python script just type 'python3 graphllm.py'.

Results are displayed on the screen and recorded in a file called 'response.txt' located in the same folder than the python script.

