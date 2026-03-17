### System Requirements

- Python 3.12 or higher  
- External TTL syntax validation tool  
- External TTL formating tool  
- Automtic reasoner (owlready2)
- Network connectivity for LLM API access

### Core Python Dependencies

- **rdflib**: RDF graph processing and SPARQL query execution
- **networkx**: Graph algorithmic analysis and structural computation
- **pyvis**: Interactive web-based graph visualization
- **openai**: Large Language Model API integration
- **owlready2**: Ontology-oriented programming packages
- **requests**: Core HTTp library for python, used for making API calls

### Environment Setup

1. **Virtual Environment Creation:**
```bash
python3 -m venv venv
source venv/bin/activate
```

2. **Dependency Installation:**  
Required packages: `requests`, `rdflib`, `openai`, `networkx`, `owlready2`; `pyvis`. Install them manually:
```bash
python3 -m pip install requests rdflib openai networkx owlready2 pyvis
```
or 
```bash
python3 -m pip install -r requirements.txt
```  
3. **External Tool Installation:**  
Install the [Turtle Validator :fontawesome-solid-external-link-alt:](https://github.com/IDLabResearch/TurtleValidator){:target="_blank" rel="noopener"} for syntax validation and the [Ontology engineering tool :fontawesome-solid-external-link-alt:](https://github.com/atextor/owl-cli){:target="_blank" rel="noopener"} for Turtle format rearrangement.


