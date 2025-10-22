''' function used to generate graphs from llm '''

import os
import shutil
import logging
from pathlib import Path
import subprocess
from openai import OpenAI, OpenAIError




def query_llm(prompt,ontology,model):
    '''quey llm API'''

    #client = genai.Client()
    client = OpenAI(api_key=os.environ.get("LLM_PROXY_KEY"),base_url="https://llmproxy.ai.orange")
    reas_eff="high"
    max_tok="not set"
    try:
        response = client.chat.completions.create(
        #response = client.completions.create(
            model=model,
            temperature=0.1, # model's creativity
            top_p=0.4, # model's creativity
            reasoning_effort=reas_eff,
            #extra_body={
            #        'extra_body': {
            #            "google": {
            #                "thinking_config": {
            #                    "thinking_budget": -1,
            #                    "include_thoughts":True
            #                }
            #            }
            #        }
            #},
            #input=prompt)
            #max_tokens=max_tok, # sum of reasoning tokens and text tokens
            #max_completion_tokens=max_tok,
            #frequency_penalty=1, #Applies a penalty to repeated tokens, reducing the likelihood of repetition in the generated text.
            #presence_penalty=1, # Applies a penalty to tokens that have already appeared in the generated text, further reducing repetition.
            #reasoning_effort="high",
            messages = [
                {   "role":"system",
                    "content":"""You are an expert in websemantic technologies and most 
                    particulary in knowledge graph and ttl format. 
                    Please provide detailed and comprehensive responses to the following queries. 
                    Ensure that your answers are as thorough as possible.
                    """
                },
                {   "role": "user",
                    "content": f"""Follow the instruction : {prompt} and use the following schema:
                    {ontology} to generate a new graph in turtle format"""
                }
                       ]
            )

        #for part in response.candidates[0].content.parts:
        #    if not part.text:
        #        continue
        #    if part.thought:
        #        print("Thought summary:")
        #        print(part.text)
        #        print()
        #    else:
        #        print("Answer:")
        #        print(part.text)
        #        print()

            #prompt=f"""Follow the instruction : {prompt} and use the following schema: {ontology} 
            #to generate a new graph in turtle format""")
    except OpenAIError as e:
        print(f"An error occured: {e}")

    #print(response.output_text)
    #print(response)
    return max_tok,reas_eff,response

def storing_results(response,temp_file,file_result):
    '''store and clean results'''

    with open(temp_file,'x',encoding='utf-8') as filetemp:
        filetemp.write(response.choices[0].message.content)
        #filetemp.write(response.choices[0].text)
        #filetemp.write(response)
        
        filetemp.close()

    #with open(temp_file, 'r',encoding='utf-8') as infile, open(file_result, 'w',encoding='utf-8')\
        # as outfile:
    #    for line in infile:
    #        if line.startswith('`'):
    #            continue
    #        cleaned_line = line.replace('<', '').replace('>', '')
    #        outfile.write(cleaned_line)
    #    infile.close()
    #    outfile.close()

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
    logger = logging.getLogger('Gen_log')
    logger.info('##################################################')

    if stdout!='Validator finished with 0 warnings and 0 errors.\n' :
    # move bad file in bad folder and Save logs

        print(f'\nFILE {Path(file_result).name} has been generated with errors')
        file=Path(file_result).name
        logger.info('\nFILE %s :',file)

        os.makedirs(f'{bad_path_result}', exist_ok=True)
        shutil.move(file_result, bad_file_result)

        with open(f'{bad_path_result}/errors.log', 'a',encoding='utf-8') as log:
            log.write(f'{bad_file_result} : {ttlvalidator.communicate()}\n')
            log.close()
    else:
    # make a copy of right files
        #folder_path = f'{os.path.dirname(file_result)}/raw_file'
        #os.makedirs(folder_path, exist_ok=True)
        #shutil.copy(file_result,folder_path)
        print(f'\nFILE {Path(file_result).name} has been generated succesffully without errors')
        logger.info('\nFILE : %s has been generated succesffully without errors',Path(file_result).name)

    if merged==1:
        print(f'Merged graph : Turtle validator Result: {stdout}'.rstrip('\n'))
        logger.info('Merged graph : Turtle validator Result: %s',stdout.rstrip('\n'))
    else:
        print(f'Turtle validator Result: {stdout}'.rstrip('\n'))
        logger.info('Turtle validator Result : %s',stdout.rstrip('\n'))

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
