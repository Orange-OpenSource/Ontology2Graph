# GenGraphLLM

graphllm.py script is dedicated to query LLM models throught the internal Orange portal [LLM PROXY Portail](https://portal.llmproxy.ai.orange/) in order to generate a knowledge graph in  turtle format based on an ontology schema . Three differents prompts have been created

   * The First one (First_prompt.txt) just needs ontologie in turtle (ttl) format.
   * The Second one (Second_prompt.txt) needs ontologie ttl file and extract of a knowledge graph based on this ontologie.
   * The Third one (Third_prompt.txt) needs ontologie ttl file and a complete knowledge graph based on this ontologie.

## Getting started

### Prerequisite

1. You need first to create an account in [LLM PROXY Portail](https://portal.llmproxy.ai.orange/).
2. Then once it is done you must setup a local environment variable called LLM_PROXY_KEY with the value of your LLM_PROXY key.

### Settings in graphllm.py

You have to set several constants in graphllm.py

1. PATH_ONTOLOGY to choose the righ ontologie ttl file.
2. PROMPT_TYPE to choose between the 3 different prompts.
3. MODEL, as awaited by the LLM_Proxy_portal, to choose your LLM. (Models's list is inserted in the script)
4. ONTO: the name of the ontology, as you want it just to mention it in the file result
5. PATH_RESULT to store the result depending on how you will use graphllm.py, just to generate one graph or to generate a series of graph.

For the third choice : 

    - PATH_GRAPH constant must be set with the location of the knowledge graph 
    - replace f"""Follow the instruction : {PROMPT} and use the following schema
                {ONTOLOGY} to generate a new graph in turtle format"""
      by f"""Follow the instruction : {PROMPT} and use the following schema
                {ONTOLOGY} and {GRAPH} to generate a new graph in turtle format"""

### Start conversion

To launch the python script just type 'python3 graphllm.py'. Results are stored in {PATH_RESULT} in turtle format.

### produce KG at regular interval

In order to produce KG at regular interval (Each five minutes) you have to setup the crontab like this :

```
    #Define environment variable
    LLM_PROXY_KEY= "YOUR LLM PROXY TOKEN"

    */5 * * * * bash "PATH TO script_crontab.sh" >> result.log 2>&1
```
script_crontab.sh must be slighlt modified depending on the location of graphllm.py

###
