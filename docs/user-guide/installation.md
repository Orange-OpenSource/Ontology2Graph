### System Requirements

- Python 3.8 or higher  
- External TTL validation tool  
- External TTL formating tool  
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
   Python 3.7+,  
   Required packages: `requests`, `rdflib`, `openai`, `networkx`, `owlready2`; `pyvis`. Install them manually:
   ```bash
   python3 -m pip install requests rdflib openai networkx owlready2 pyvis
   ```
   or 
   ```bash
   python3 -m pip install -r requirements.txt
   ```  
3. **External Tool Installation:**  
Install the [Turtle Validator](https://github.com/IDLabResearch/TurtleValidator) for syntax validation and the [Ontology engineering tool](https://github.com/atextor/owl-cli) for Turtle format rearrangement.

