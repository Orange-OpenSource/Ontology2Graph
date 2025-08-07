# GenGraphLLM

GenGraphLLM is a set of python scripts that create synthetic Knowledge Graphs based on LLM queries. GenGraphLLM is also able to compute Knowledge Graph KPIs and display the Graph Generated.

**graphllm.py** script is dedicated to query LLM models throught the internal Orange portal [LLM PROXY Portail](https://portal.llmproxy.ai.orange/) in order to generate a knowledge graph in turtle (ttl) format based on an ontology ttl schema. A validation turtle syntax step is integrated in the graph generation process. Three differents prompts have been elaborated and are available in the 'prompts' folder. 

   * The First one (First_prompt.txt) just needs and ontologie ttl format.
   * The Second one (Second_prompt.txt) needs ontologie ttl file and an extract of a knowledge graph based on this ontologie.
   * The Third one (Third_prompt.txt) needs ontologie ttl file and a complete knowledge graph based on this ontologie.

**graph_kpis_display.py** script compute some specific Knowledge Graphs KPIs and dysplay the graph in your brower

**utils.py** script is a collection of functions used by graph_kpis_display.py

## Getting started

### GenGraphLLM installation

To install GenGraphLLM in your local environment, clone this repository, create and launch a virtual python environement.

```
python3 -m venv .
source /bin/activate
```

and intall all the packages listed in requirements.txt file

```
python3 -m pip install -r requirements.txt
```

### Prerequisite to generate a synthetic Knowledge Graph

1. First, you need to create an account in [LLM PROXY Portail](https://portal.llmproxy.ai.orange/). Then once it is done you must setup a local environment variable called LLM_PROXY_KEY with the value of your LLM_PROXY key.
2. Second you must install the following [turtle validator](https://github.com/IDLabResearch/TurtleValidator) in your environment. 
3. You have to set several constants in graphllm.py

    1. PATH_ONTOLOGY to choose the righ ontologie ttl file.
    2. PROMPT_TYPE to choose between the 3 different prompts.
    3. MODEL, as awaited by the LLM_Proxy_portal, to choose your LLM. (Models's list is inserted in the script)
    4. ONTO: the name of the ontology, as you want it just to mention it in the file result
    5. PATH_RESULT to store the result depending on how you will use graphllm.py, just to generate one graph or to generate a series of graph.

    For the second and the third prompt you have to do the following : 

        - PATH_GRAPH constant must be set with the location of the knowledge graph 
        - in graphllm.py :  replace f"""Follow the instruction : {PROMPT} and use the following schema
                            {ONTOLOGY} to generate a new graph in turtle format"""
                            by f"""Follow the instruction : {PROMPT} and use the following schema
                            {ONTOLOGY} and {GRAPH} to generate a new graph in turtle format"""

### Start conversion

To launch the python script once for all, just type 'python3 graphllm.py'. Results are stored in {PATH_RESULT} in turtle format 

### Produce KG at regular interval

In order to produce Knowledge Graphs at regular intervals (Each five minutes for instance) you have to setup the crontab like this :

```
    #Define environment variable
    LLM_PROXY_KEY= "YOUR LLM PROXY TOKEN"

    */5 * * * * bash "PATH TO script_crontab.sh" >> result.log 2>&1
```
script_crontab.sh must be slighlty modified depending on the location of graphllm.py

With this crontab settings graphllm.py will produce Knowledge Graphs at regular intervals and a result.log file with the following content : 

```
	2025-07-02_15-54-01 vertex_ai/gemini-2.0-flash 
	Prompt tokens :  35448
	Output response tokens 3812
	Turtle validator Result: ('Validator finished with 0 warnings and 0 errors.\n', '')
	2025-07-02_15-56-01 vertex_ai/gemini-2.0-flash
	Prompt tokens :  35448
	Output response tokens 1694
	Turtle validator Result: ('Validator finished with 0 warnings and 0 errors.\n', '')
	...
```

### Merge Knmowledge Graph 

TBD

