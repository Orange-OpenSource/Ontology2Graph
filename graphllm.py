""" Generate knowledge graph in turtle format based on schema, using the internal Orange LLM Proxy 
portal (https://portal.llmproxy.ai.orange/)"""

import os
from openai import OpenAI, OpenAIError

#PATH="/mnt/c/Users/piod7321/Downloads/results"
PATH="/home/piod7321/DIGITAL_TWIN/gengraphllm/results"
#MODEL="vertex_ai/gemini-2.0-flash" 
#MODEL='openai/gpt-4.1-mini'
#MODEL='vertex_ai/claude3.7-sonnet'
#MODEL='openai/o1-preview'
#MODEL='openai/o3'
#MODEL='openai/gpt-4.1-nano'
#MODEL='openai/gpt-4.1'
#MODEL='vertex_ai/gemini-1.5-flash'
#MODEL='openai/o4-mini'
#MODEL='openai/gpt-4o'
#MODEL='vertex_ai/gemini-1.5'
#MODEL="openai/gpt-4o-mini"
#MODEL="openai/o3-mini"
#MODEL="vertex_ai/claude3.5-sonnet-v2"
#MODEL="openai/o1"
#MODEL="vertex_ai/codestral" #no answer
#MODEL="openai/o1-mini"
MODEL="openai/gpt-3.5-turbo"

client = OpenAI(api_key=os.environ.get("ORANGE_LLM_PROXY_KEY"),
                base_url="https://llmproxy.ai.orange")

with open('schema.ttl','rt',encoding='utf-8') as TTL:
    TTL_SCHEMA = ','.join(str(x) for x in TTL.readlines())

with open('Third_instructions.txt','rt',encoding='utf-8') as file_instructions:
    INSTRUCTION = ','.join(str(x) for x in file_instructions.readlines())

with open('full_graph.ttl','rt',encoding='utf-8') as file_instructions:
    GRAPH = ','.join(str(x) for x in file_instructions.readlines())

try:
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.1, # increase model's creativity
        top_p=0.1, # increase model's creativity
        messages = [
            {   "role":"system",
                "content":"""You are an expert in websemantic technologies and most particulary in knowledge graph and ttl format"""
            },
            {   "role": "user",
                "content": f"""Follow the instruction : {INSTRUCTION} and use the following schema:
                {TTL_SCHEMA} and graph : {GRAPH} as en example to generate a new graph in turtle format"""
            }
        ]
    )
    
    with open(PATH + f'/Third_graph_{response.model}.ttl','w',encoding='utf-8') as f:
        f.write(response.choices[0].message.content)

## remove useless character
    with open(PATH + f'/Third_graph_{response.model}.ttl', 'r') as file:
        lines = file.readlines()

    # Check if the first line starts with the specific character
    if lines and lines[0].startswith('`'):
        # Remove the first line
        lines = lines[1:]
        # Remove the last line
        lines = lines[:-1]

        # Write the remaining lines back to the file
        with open(PATH + f'/Third_graph_{response.model}.ttl', 'w') as file:
            file.writelines(lines)

## print file content

    with open(PATH + f'/Third_graph_{response.model}.ttl', 'r') as file:
        contents = file.read()
        print(contents)

except OpenAIError as e:
    print(f"An error occured: {e}")
