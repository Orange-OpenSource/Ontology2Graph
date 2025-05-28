""" Generate knowledge graph in turtle format based on schema, using the internal Orange LLM Proxy 
portal (https://portal.llmproxy.ai.orange/)"""

import os
from openai import OpenAI, OpenAIError

GENERATED_GRAPH = 'results/Third_generated_graph.ttl'


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
        #model="openai/gpt-3.5-turbo",
        model="vertex_ai/gemini-2.0-flash",
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
    
    with open(GENERATED_GRAPH,'w',encoding='utf-8') as f:
        f.write(response.choices[0].message.content)


## remove useless character
    with open(GENERATED_GRAPH, 'r') as file:
        lines = file.readlines()

    # Check if the first line starts with the specific character
    if lines and lines[0].startswith('`'):
        # Remove the first line
        lines = lines[1:]
        # Remove the last line
        lines = lines[:-1]

        # Write the remaining lines back to the file
        with open(GENERATED_GRAPH, 'w') as file:
            file.writelines(lines)

## print file content

    with open(GENERATED_GRAPH, 'r') as file:
        contents = file.read()
        print(contents)

except OpenAIError as e:
    print(f"An error occured: {e}")
