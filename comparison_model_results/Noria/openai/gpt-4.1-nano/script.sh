# This script launch several robot command on knowledge graph
# $1 argument correspond the time when the script has been launch in the following format hh:mm:ss
# it must be pass to the script like that "bash script.sh hh:mm:ss"

robot measure --input First_graph_noria_2025-06-26_$1_gpt-4.1-nano-2025-04-14.ttl --metrics all --format csv --output First_graph_noria_2025-06-26_$1_gpt-4.1-nano-2025-04-14_measure.csv

robot reason --reasoner ELK --input First_graph_noria_2025-06-26_$1_gpt-4.1-nano-2025-04-14.ttl --output First_graph_noria_2025-06-26_$1_gpt-4.1-nano-2025-04-14_reason.owl

robot report --input First_graph_noria_2025-06-26_$1_gpt-4.1-nano-2025-04-14.ttl --label true --output First_graph_noria_2025-06-26_$1_gpt-4.1-nano-2025-04-14_report.tsv

robot export --input First_graph_noria_2025-06-26_$1_gpt-4.1-nano-2025-04-14.ttl --header "ID|IRI|LABEL" --export First_graph_noria_2025-06-26_$1_gpt-4.1-nano-2025-04-14_export.tsv
