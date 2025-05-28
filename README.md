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

### Settings

You have 3 differents choices to generate a new graph. 

1. Only with the schema.ttl file provided (First_instruction.txt)  
2. With schema.ttl and an extract of a graph based on this schema (Second_instruction.txt)
3. With schema.ttl and a full graph based on this shcema (Third_instruction.txt)

You have to slightly modify graphllm.py depending on your choice.

 - Constant GENERATED_GRAPH
 - Name of the instruction file
 - For the third choice don't forget top add the constant GRAPH in "messages" as a full example of knowledge graph  

### Start conversion

To launch the python script just type 'python3 graphllm.py'.
Results are displayed on the screen and recorded in the results folder.

