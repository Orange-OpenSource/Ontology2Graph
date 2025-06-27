# GenGraphLLM

graphllm.py script is dedicated to query LLM models throught the internal Orange portal [LLM PROXY Portail](https://portal.llmproxy.ai.orange/) in order to generate a knowledge graph in  turtle format based on an ontology schema . Three differents prompts have been created

   * The First one gives the schema and provides some explanantions.
   * The Second one gives the schema and an extract of a knowledge graph, and provides some explanantions.
   * The Third one gives the schema and a complete knowledge graph, and provides some explanantions.

## Getting started

### Prerequisite

1. You need first to create an account in [LLM PROXY Portail](https://portal.llmproxy.ai.orange/).
2. Then once it is done you must setup a local environment variable called ORANGE_LLM_PROXY_KEY with the value of your LLM_PROXY key.

### Settings in graphllm.py

You have to set several constants in graphllm.py

1. PATH_RESULT to store the result.
2. PROMPT_TYPE to choose between the 3 different prompts.
3. ONTO: the name of the ontology, as you want it just to mention it in the file result
2. MODEL, as awaited by the LLM_Proxy_portal, to choose your LLM. (Models's list is inserted in the script)

You have 3 differents choices to generate a new graph. 

4. Only with the schema.ttl file provided (First_instruction.txt).
5. With schema.ttl and an extract of a graph based on this schema (Second_instruction.txt).
6. With schema.ttl and a full graph based on this schema (Third_instruction.txt).

and the localisation of the schema file must be declared in TTL_SCHEMA 

For the third choice : 

    - GRAPH must be set with the localisation of the knowledge graph 
    - add GRAPH in The prompt ("messages")  as a full example of knowledge graph  

### Start conversion

To launch the python script just type 'python3 graphllm.py'.
Results are displayed on the screen and recorded in the results folder (/results/{MODEL}/Third_graph_{DATE}_{response.model}.ttl)


### produce KG at regular interval

In order to produce KG at regular interval you have to setup the crontab like this :

```
    #Define environment variable
    ORANGE_LLM_PROXY_KEY= YOUR LLM PROXY TOKEN

    */5 * * * * bash "PATH TO script_crontab.sh" >> result.log 2>&1
```

