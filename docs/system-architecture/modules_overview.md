
The framework is structured into four primary modules:

### 1. Knowledge Graph Generation Module
<p style="text-align: justify;">
The generation module serves as the core component for synthetic knowledge graph creation. It interfaces with various Large Language Models through standardized APIs to transform ontological schemas into RDF-compliant Turtle format graphs.
</p>

### 2. Graph Consolidation Module
<p style="text-align: justify;">
The consolidation module implements algorithms for intelligent merging of multiple knowledge graphs while maintaining semantic consistency and managing duplicate entities.
</p>

### 3. Visualization and Analysis Module
<p style="text-align: justify;">
This module provides comprehensive analytical capabilities for knowledge graph assessment and interactive visualization generation.
</p>

### 4. Common Utilities Module
<p style="text-align: justify;">
Shared infrastructure components providing fundamental operations across all modules.
</p>

### 5. Schema

<div style="text-align: center;">
```mermaid
graph TD
    A[Prompt generation] --> C[Knowledge graph generation module]:::highlight
    B[Ontology] --> C
    toto[model name] --> C
    C --> D[Graph consolidation module]:::highlight
    D --> E[Visualisation module]:::highlight
    C --> E
    classDef highlight fill:#f9d423,stroke:#333,stroke-width:4px;
```
</div>




