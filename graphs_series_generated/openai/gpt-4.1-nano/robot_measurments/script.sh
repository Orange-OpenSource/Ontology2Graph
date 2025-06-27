# This script launc several robot command on knowledge graph

robot measure --input ../Third_graph_2025-06-24_$1_gpt-4.1-nano-2025-04-14.ttl --metrics all --format csv --output measurement/Third_graph_2025-06-24_$1_gpt-4.1-nano-robot_measurement.csv -vvv

robot reason --reasoner ELK --input ../Third_graph_2025-06-24_$1_gpt-4.1-nano-2025-04-14.ttl --output reason/Third_graph_2025-06-24_$1_gpt-4.1-nano-robot_reason.owl

robot report --input ../Third_graph_2025-06-24_$1_gpt-4.1-nano-2025-04-14.ttl --label true --output report/Third_graph_2025-06-24_$1_gpt-4.1-nano-robot_report.tsv

robot export --input ../Third_graph_2025-06-24_$1_gpt-4.1-nano-2025-04-14.ttl --header "ID|IRI|LABEL" --export export/Third_graph_2025-06-24_$1_gpt-4.1-nano-robot_export.tsv
