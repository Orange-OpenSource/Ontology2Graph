# This script launch several robot command on knowledge graph
# $1 argument correspond the time when the script has been launch in the following format hh:mm:ss
# it must be pass to the script like that "bash script.sh hh:mm:ss"

robot measure --input First_graph_noria_2025-06-20_$1_gemini-2.0-flash-001.ttl --metrics all --format csv --output First_graph_noria_2025-06-20_$1_gemini-2.0-flash-001_measure.csv

robot reason --reasoner ELK --input First_graph_noria_2025-06-20_$1_gemini-2.0-flash-001.ttl --output First_graph_noria_2025-06-20_$1_gemini-2.0-flash-001_reason.owl

robot report --input First_graph_noria_2025-06-20_$1_gemini-2.0-flash-001.ttl --label true --output First_graph_noria_2025-06-20_$1_gemini-2.0-flash-001_report.tsv

robot export --input First_graph_noria_2025-06-20_$1_gemini-2.0-flash-001.ttl --header "ID|IRI|LABEL" --export First_graph_noria_2025-06-20_$1_gemini-2.0-flash-001_export.tsv
