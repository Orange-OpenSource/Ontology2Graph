
''' This script concatenate the transposed file, it must be placed in the same 
directory than the transposed files '''

import os
import pandas as pd

# Define Constant
DIRECTORY=os.path.dirname(os.path.abspath(__file__))
FILE_NAME = 'concatenated_file.csv'
SEARCH_STRING = 'transposed'
CONCATENATED_FILE=DIRECTORY+'concatenate_file.csv'

# Retrieve all files transposed file
matching_files = [file for file in os.listdir(DIRECTORY) if SEARCH_STRING in file]

# initiate the concatenated file and remove the first value of matching file
concatenated_df = pd.read_csv(matching_files[0])
del matching_files[0]

# Concat the matching files
for file in matching_files:
    df = pd.read_csv(file)
    # Append the data to the concatenated DataFrame
    concatenated_df = pd.concat([concatenated_df, df], axis=0,ignore_index=True)

# Remove some columns
df_final=concatenated_df.drop(columns=['abox_nominals','abox_nominals_incl','axiom_type_count',
                                       'axiom_type_count.1','axiom_type_count_incl',
                                       'axiom_type_count_incl.1','axiom_types','axiom_types.1',
                                       'axiom_types_incl','axiom_types_incl.1','axiom_types_incl',
                                       'certain_cycle','certain_cycle_incl',
                                       'class_expression_count','class_expression_count_incl',
                                       'curie_map','curie_map.1','curie_map.2',
                                       'datatypes_builtin','datatypes_builtin_incl',
                                       'namespace_axiom_count','namespace_axiom_count.1',
                                       'namespace_axiom_count_incl','namespace_axiom_count_incl.1',
                                       'namespace_entity_count','namespace_entity_count.1',
                                       'namespace_entity_count.2','namespace_entity_count.3',
                                       'namespace_entity_count_incl',
                                       'namespace_entity_count_incl.1',
                                       'namespace_entity_count_incl.2',
                                       'namespace_entity_count_incl.3',
                                       'ontology_iri','ontology_version_iri','owl2','owl2_dl',
                                       'owl2_el','owl2_ql','owl2_rl','owl2dl_profile_violation',
                                       'owl2dl_profile_violation.1','rdfs','syntax','tbox_nominals',
                                       'tbox_nominals_incl'])

# Write the concatenated DataFrame to a new CSV file
df_final.to_csv(FILE_NAME, index=False)
print(f"CSV files have been concatenated into {FILE_NAME} without additional headers.")
