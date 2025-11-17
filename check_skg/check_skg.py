''' This python script check the consistency of synthetic knowlege graph with his ontology
You have to pass as parameter the graphs and ontologie location and the reasoner name "Pellet" 
or HermiT'''

import logging
from pathlib import Path
import argparse
import shutil
import os
import rdflib
from owlready2 import get_ontology,sync_reasoner_hermit,sync_reasoner_pellet
from owlready2 import OwlReadyInconsistentOntologyError,default_world

parser = argparse.ArgumentParser()
parser.add_argument("graph")
parser.add_argument("ontology")
parser.add_argument('reasonner')
args = parser.parse_args()

path_graph_file=args.graph
ontology=args.ontology
reasonner=args.reasonner

path_cwd=Path(f'{os.getcwd()}')
CONCAT = f'{path_cwd}/concat.ttl'

if Path(path_graph_file).is_file():
    print('this is a single file')
    path_check_log=Path(f'{Path(path_graph_file).parent}/check_graph_log')
    all_graph_to_check = [path_graph_file]
    path_graph_file=Path(path_graph_file).parent
else :
    path_check_log=Path(f'{path_graph_file}/check_graph_log')
    #all_graph_to_check = [f.name for f in Path(path_graph_file).iterdir() if f.is_file()]
    all_graph_to_check = [f for f in Path(path_graph_file).iterdir() if f.is_file()]


if os.path.exists(path_check_log):
    shutil.rmtree(path_check_log)
os.makedirs(path_check_log)

log_file=Path(f'{path_check_log}/check_graph.log')
#print(log_file)

#if log_file.is_file():
#    print('toto')
#    os.remove(log_file)

logger_check = logging.getLogger('check_graph_log')
handler = logging.FileHandler(log_file)
logger_check.setLevel(logging.DEBUG)
logger_check.addHandler(handler)

for graph_to_check in all_graph_to_check :
    print(graph_to_check)
#concat ontology and graph in the same file

    CONCATENATED_CONTENT=""
    TARGET_FILE="concatenated_file.ttl"

    #for source_file in [graph_to_check,ontology]:
    #    with open(source_file, 'r', encoding='utf-8') as file:
    #        CONCATENATED_CONTENT += file.read() + "\n"

    #with open(TARGET_FILE,'w',encoding='utf-8') as final_file:
    #    final_file.write(CONCATENATED_CONTENT)

    with open(CONCAT, 'w', encoding='utf-8') as target_file:
        for source_file in [ontology,graph_to_check]:
            with open(source_file, 'r', encoding='utf-8') as file_source:
                for line in file_source:
                    target_file.write(line)

    skgraph = rdflib.Graph()
    #skgraph.parse(TARGET_FILE, format="turtle")
    skgraph.parse(f"file://{CONCAT}", format="turtle")

# Convert RDFLib graph to OWL/XML format
    graph_xml = skgraph.serialize(format="xml")
    encoded_graph = graph_xml.encode('utf-8')

# Save the OWL/XML graph to a temporary file
    with open(f'temp_graph.owl{Path(graph_to_check).name}', "wb") as temp_graph_owl:
        temp_graph_owl.write(encoded_graph)

    #OUTPUT_LOG = f'{path_cwd}/owlready_{graph_to_check}_output.log'
    #ERROR_LOG = f'{path_cwd}/owlready_{graph_to_check}_error.log'

    encoded_graph_to_check=get_ontology(f'file://temp_graph.owl{Path(graph_to_check).name}').load()

    #sys.stdout = open('owlready_output.log', 'a', encoding='utf-8')
    #sys.stderr = open('owlready_error.log', 'a', encoding='utf-8')
    logger_check.info('##########################################################################')
    logger_check.info('Graph : %s \n',Path(graph_to_check).name)

    try:
        with encoded_graph_to_check:
            if reasonner=="HermiT":
                sync_reasoner_hermit(debug=2, keep_tmp_file=True,
                                      ignore_unsupported_datatypes = True)
            if reasonner=="Pellet":
                sync_reasoner_pellet(debug=2, keep_tmp_file=True,
                                    infer_property_values=True,infer_data_property_values=True)
    except OwlReadyInconsistentOntologyError as OntoE:
        print(f'\nOwlReadyInconsistentOntologyError detected by {reasonner} for {Path(graph_to_check).name}')
        logger_check.info('OwlReadyInconsistentOntologyError detected by : %s \n',reasonner)
        logger_check.info(OntoE)

    except OverflowError as e: #system ressource limits reach
        print(f"\nOverFlowError : {e}")
        logger_check.info('OverFlowError : %s',e)

    else :
        print(f'\nNo inconsistent Ontology errors detected by {reasonner} for {Path(graph_to_check).name}\n')
        logger_check.info('No inconsistent Ontology errors found by %s ',reasonner)
# list classes inferred equivalent to owl:Nothing (unsatisfiable classes)
    unsat = list(default_world.inconsistent_classes())
    if unsat:
        print(f'inconsistent classes found by {reasonner} :\n')
        for c in unsat:
            print(" - \n", c)
            logger_check.info('inconsistent classes found by %s',reasonner)
            logger_check.info(' %s',c)
    else:
        print(f'No inconsistent classes found by {reasonner} for {Path(graph_to_check).name}.\n')
        logger_check.info('No inconsistent classes found by %s',reasonner)

    logger_check.info('##########################################################################')

    target_file.close()
    file_source.close()
    temp_graph_owl.close()
# remove CONCAT file
    if Path(CONCAT).is_file():
        os.remove(Path(CONCAT))
# remove temp_graph_owl
    if Path(f'{path_cwd}/temp_graph.owl').is_file():
        os.remove(Path(f'{path_cwd}/temp_graph.owl'))
