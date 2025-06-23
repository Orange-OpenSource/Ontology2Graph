# This script launc several robot command on knowledge graph

#robot measure --input ../Third_graph_2025-06-16_16-$1_gpt-4.1-2025-04-14.ttl --metrics all --format csv --output measurement/Third_graph_2025-06-16_16-$1_gpt-4.1-robot_measurement.csv

robot reason --reasoner ELK --input ../Third_graph_2025-06-16_16-$1_gpt-4.1-2025-04-14.ttl --output reason/Third_graph_2025-06-16_16-$1_gpt-4.1-robot_reason.owl

robot report --input ../Third_graph_2025-06-16_16-$1_gpt-4.1-2025-04-14.ttl --label true --output report/Third_graph_2025-06-16_16-$1_gpt-4.1-robot_report.tsv

robot export --input ../Third_graph_2025-06-16_16-$1_gpt-4.1-2025-04-14.ttl --header "ID|IRI|LABEL" --export export/Third_graph_2025-06-16_16-$1_gpt-4.1-robot_export.tsv
