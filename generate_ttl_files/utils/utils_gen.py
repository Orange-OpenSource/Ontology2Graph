''' function used to generate graphs from llm '''

import os
import shutil
from pathlib import Path
import subprocess
from openai import OpenAI, OpenAIError

def query_llm(prompt,ontology,model):
    '''quey llm API'''

    client = OpenAI(api_key=os.environ.get("LLM_PROXY_KEY"),base_url="https://llmproxy.ai.orange")

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.1, # model's creativity
            top_p=0.1, # model's creativity
            messages = [
                {   "role":"system",
                    "content":"""You are an expert in websemantic technologies and most 
                    particulary in knowledge graph and ttl format"""
                },
                {   "role": "user",
                    "content": f"""Follow the instruction : {prompt} and use the following schema:
                    {ontology} to generate a new graph in turtle format"""
                }
                        ]
                                                )

    except OpenAIError as e:
        print(f"An error occured: {e}")

    return response

def storing_results(response,temp_file,file_result):
    '''store and clean results'''

    with open(temp_file,'x',encoding='utf-8') as filetemp:
        filetemp.write(response.choices[0].message.content)
        filetemp.close()

    #Remove lines start with '
    with open(temp_file,'r',encoding='utf-8') as file:
        lines = file.readlines()
        filtered_lines = [lines for lines in lines if not lines.startswith('`')]
        file.close()

    with open(file_result,'w',encoding='utf-8') as final:
        final.writelines(filtered_lines)
        final.close()

    os.remove(temp_file)

def check_ttl(file_result, bad_file_result, bad_path_result,merged):
    '''check ttl syntax store wrong file in specific folder and 
    maek a copy of right ttl file'''
    command=["ttl",file_result]
    ttlvalidator = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    stdout, stderr = ttlvalidator.communicate()

    if stdout!='Validator finished with 0 warnings and 0 errors.\n' :
    # move bad file in bad folder and Save logs

        print(f'\nFILE {Path(file_result).name} has been generated with errors')

        os.makedirs(f'{bad_path_result}', exist_ok=True)
        shutil.move(file_result, bad_file_result)

        with open(f'{bad_path_result}/errors.log', 'a',encoding='utf-8') as log:
            log.write(f'{bad_file_result} : {ttlvalidator.communicate()}\n')
            log.close()
    else:
    # make a copy of right files
        folder_path = f'{os.path.dirname(file_result)}/raw_file'
        os.makedirs(folder_path, exist_ok=True)
        shutil.copy(file_result,folder_path)
        print(f'\nFILE {Path(file_result).name} has been generated succesffully without errors')

    if merged==1:
        print(f'Merged graph : Turtle validator Result: {stdout}'.rstrip('\n'))
    else:
        print(f'Turtle validator Result: {stdout}'.rstrip('\n'))

def ttl_validator(path):
    '''validate ttl merged graph'''
    all_files = [f.name for f in Path(path).iterdir() if f.is_file()]

    for i, file in enumerate(all_files):
        all_files[i]= path + file

    for file in all_files :
        command=["ttl",file]
        ttlvalidator=subprocess.Popen(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                      text=True)
        stdout, stderr = ttlvalidator.communicate()
        print(file)
        print(f'Merged graph : Turtle validator Result: {stdout},{stderr}')
        print('\n')
