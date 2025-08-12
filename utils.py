'''list of function to be used '''

import webbrowser
import os
import datetime
import shutil
from pathlib import Path
import subprocess
from pyvis.network import Network
from openai import OpenAI, OpenAIError

def remove_pred_obj(expr, graph, predi, obje):
    '''remove predicate and target object of an edge'''
    edges_to_remove = [(u, v) for u, v, attr in graph.edges(data=True)
                         if attr.get(expr) == predi and v == obje]
    return graph.remove_edges_from(edges_to_remove)

def get_last_folder_part(string, sep_char):
    """get last part of a folder string"""
    string_parts=string.split(sep_char)
    last_part=string_parts[len(string_parts)-1]
    if last_part=='':
        last_part=string_parts[len(string_parts)-2]
    return last_part

def retreive_datatype_properties(ontology):
    '''create a list of all the data type properties from the ontologie'''

    index_list=[]
    dtprop=[]
    dtproperties=[]

    #build index list of DatatypeProperty
    with open(f'{ontology}', 'r',encoding='utf-8') as file:
        for index, line in enumerate(file, start=1):
            if 'DatatypeProperty' in line :
                index_list.append(index-1)
    file.close()

    #retreive DatatypeProperties based on index list
    with open(f'{ontology}', 'r',encoding='utf-8') as file:
        for index, line in enumerate(file, start=1):
            if index in index_list:
                dtprop.append(line.strip())
                #print(line.strip())
    file.close()

    #clean DatatypeProperties
    for dtp in dtprop:
        dtp=dtp.replace('noria:',"")
        dtproperties.append(dtp)
    return dtproperties

def display_graph(graph,model):
    '''dysplay the graph'''

    path=os.getcwd()
    date_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    net = Network(height="840px", width="100%", bgcolor="#222222", font_color="white",
                  directed=True,neighborhood_highlight=True)

    net.barnes_hut()
    net.from_nx(graph)
    net.show_buttons(filter_=['physics'])

    outputfile=f'{path}/results/HTML_graph/knowledge_graphe_{date_time}_{model}.html'
    net.save_graph(outputfile)
    full_path=os.path.abspath(outputfile)
    print('full path',full_path)

    webbrowser.open(f'file://///wsl.localhost/Ubuntu-24.04{full_path}',autoraise=True)
    #webbrowser.open(full_path,autoraise=True)

def query_llm(date_time,prompt,ontology,model):
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
        print(f'{date_time} {model}')
        print("Prompt tokens : ",response.usage.prompt_tokens)
        print("Output response tokens", response.usage.completion_tokens)

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

def check_ttl(file_result, bad_file_result, bad_path_result):
    '''check ttl syntax and store wrong file in specific folder'''
    command=["ttl",file_result]
    ttlvalidator=subprocess.Popen(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    stdout, stderr = ttlvalidator.communicate()
    print(f'Turtle validator Result: {ttlvalidator.communicate()}')

    if stdout!='Validator finished with 0 warnings and 0 errors.\n' :
    # move bad file in bad folder and Save logs

        os.makedirs(f'{bad_path_result}', exist_ok=True)
        shutil.move(file_result, bad_file_result)

        with open(f'{bad_path_result}/errors.log', 'a',encoding='utf-8') as log:
            log.write(f'{bad_file_result} : {ttlvalidator.communicate()}\n')
            log.close()

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
