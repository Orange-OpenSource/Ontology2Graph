""" This python script generates knowledge graph in turtle format based on an ontology schema, a 
prompt and/or a graph example. It uses the internal Orange LLM Proxy portal 
(https://portal.llmproxy.ai.orange/) for which you must have an account. Several constant must be
set directly in this script before launching
"""
import os
import datetime
import subprocess
import shutil
from openai import OpenAI, OpenAIError

DATE = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# PATH constant where are stored the needed ressources, prompt, ontology and graph
PATH=os.getcwd()
#PATH=f'{os.getcwd()}/DIGITAL_TWIN/gengraphllm' # when using crontab
PATH_ONTOLOGY=f'{PATH}/ontologies'
PATH_PROMPT=f'{PATH}/prompts'
PATH_GRAPH=f'{PATH}/graph'

## PROMPT_TYPE to choose ##
PROMPT_TYPE='First_prompt'
#PROMPT_TYPE='Second_prompt'
#PROMPT_TYPE='Third_prompt'

## ONTOLOGY to choose ##
ONTO='Noria'
#ONTOLOGY='pygraph'

## MODEL constant to choose ##

MODEL="vertex_ai/gemini-2.0-flash"
#MODEL='openai/gpt-4.1-mini'
#MODEL='vertex_ai/claude3.7-sonnet'
#MODEL='openai/o1-preview'
#MODEL='openai/o3'
#MODEL='openai/gpt-4.1-nano'
#MODEL='openai/gpt-4.1'
#MODEL='vertex_ai/gemini-1.5-flash'
#MODEL='openai/o4-mini'07
#MODEL='openai/gpt-4o'
#MODEL='vertex_ai/gemini-1.5'
#MODEL="openai/gpt-4o-mini"
#MODEL="openai/o3-mini"
#MODEL="vertex_ai/claude3.5-sonnet-v2"
#MODEL="openai/o1"
#MODEL="vertex_ai/codestral" #no answer
#MODEL="openai/o1-mini"
#MODEL="openai/gpt-3.5-turbo"

#PATH result to choose
#PATH_RESULT=f'{PATH}/graphs_generated_by_models/{MODEL}'
PATH_RESULT=f'{PATH}/graphs_time_series_generated/{MODEL}'

os.makedirs(f'{PATH_RESULT}/',exist_ok=True)

BAD_PATH_RESULT=f'{PATH_RESULT}/Bad_Turtle_Syntax'

client = OpenAI(api_key=os.environ.get("LLM_PROXY_KEY"),base_url="https://llmproxy.ai.orange")

with open(f'{PATH_ONTOLOGY}/Noria.ttl','rt',encoding='utf-8') as ontology:
    ONTOLOGY = ','.join(str(x) for x in ontology.readlines())

with open(f'{PATH_PROMPT}/{PROMPT_TYPE}.txt','rt',encoding='utf-8') as prompt:
    PROMPT = ','.join(str(x) for x in prompt.readlines())

# Only for second and third prompt
with open(f'{PATH_GRAPH}/full_graph.ttl','rt',encoding='utf-8') as graph:
    GRAPH = ','.join(str(x) for x in graph.readlines())

try:
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.1, # model's creativity
        top_p=0.1, # model's creativity
        messages = [
            {   "role":"system",
                "content":"""You are an expert in websemantic technologies and most 
                particulary in knowledge graph and ttl format"""
            },
            {   "role": "user",
                "content": f"""Follow the instruction : {PROMPT} and use the following schema:
                {ONTOLOGY} to generate a new graph in turtle format"""
            }
        ]
    )

    print(f'{DATE} {MODEL}')
    print("Prompt tokens : ",response.usage.prompt_tokens)
    print("Output response tokens", response.usage.completion_tokens)

    #Write the result in a temporary file
    with open(f'{PATH_RESULT}/{PROMPT_TYPE}_temp.ttl','x',encoding='utf-8') as filetemp:
        filetemp.write(response.choices[0].message.content)
        filetemp.close()

    #Remove lines start with '
    with open(f'{PATH_RESULT}/{PROMPT_TYPE}_temp.ttl','r',encoding='utf-8') as file:
        lines = file.readlines()
        filtered_lines = [lines for lines in lines if not lines.startswith('`')]
        file.close()

    #save filtered result
    with open(f'{PATH_RESULT}/{PROMPT_TYPE}_{DATE}_{ONTO}.ttl','w',encoding='utf-8') as filtered:
        filtered.writelines(filtered_lines)
        filtered.close()

    os.remove(f'{PATH_RESULT}/{PROMPT_TYPE}_temp.ttl')

    # Check Turtle syntax
    command=["ttl",f'{PATH_RESULT}/{PROMPT_TYPE}_{DATE}_{ONTO}.ttl']
    ttlvalidator=subprocess.Popen(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    stdout, stderr = ttlvalidator.communicate()
    print(f'Turtle validator Result: {ttlvalidator.communicate()}')

    if stdout!='Validator finished with 0 warnings and 0 errors.\n' :
        # move bad file in bad folder and Save logs

        os.makedirs(f'{BAD_PATH_RESULT}', exist_ok=True)
        shutil.move(f'{PATH_RESULT}/{PROMPT_TYPE}_{DATE}_{ONTO}.ttl',
                    f'{BAD_PATH_RESULT}/{PROMPT_TYPE}_{DATE}_{ONTO}_BAD.ttl')

        with open(f'{BAD_PATH_RESULT}/errors.log', 'a',
                       encoding='utf-8') as log:
            log.write(f'{PROMPT_TYPE}_{DATE}_{ONTO}_BAD.ttl : {ttlvalidator.communicate()}\n')
            log.close()

except OpenAIError as e:
    print(f"An error occured: {e}")
