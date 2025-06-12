This table compare the results of differents Knowledge Graph build with different LLM. KG have been built the 11th of June 2025.
It is important to notice that the same LLM doesn't provide always exactly the same result due to the statiscal nature of LLMs


|     Model             |   Consistent with the prompt      |  Number of <br> Classes|  Number of <br> Nodes      |  useable in <br> Protégé   | HermiT <br>Consitency | ROBOTS <br>measurments |
|:---------------------:|:---------------------------------:|:----------------------:|:--------------------------:|:--------------------------:|:---------------------:|:----------------------:|
|Claude-3.5-sonnet*     |No, comments                       |            9           |             9              |           yes              |         yes           |          yes           |
|Claude-3.7-sonnet*     |No, comments + truncated           |           10           |            51              |           yes              |         yes           |          yes           |                       
|Gemini-1.5-flash       |Yes                                |           10           |            10              |           yes              |         yes           |          yes           |
|Gemini-1.5-pro*        |No, comments + isolated Nodes       |            8           |            18              |           yes              |         yes           |          yes           |
|Gemini-2.0-flash       |Yes                                |           10           |            14              |           yes              |         yes           |          yes           |
|gpt-4.1                |Yes                                |            9           |           123              |           yes              |         yes           |          yes           |
|gpt-4.1-mini           |Yes                                |            8           |            22              |           yes              |         yes           |          yes           |
|**gpt-4.1-nano**       |Yes                                |            7           |            16              |           yes              |         yes           |          yes           |
|gpt-4o*                |No, comments                       |           10           |            24              |           yes              |         yes           |          yes           |
|gpt-4o-mini            |Yes                                |            1           |            14              |           yes              |         yes           |          yes           |
|o1                     |No, isolated nodes                 |            6           |             8              |           yes              |         yes           |          yes           |
|o1-mini                |Yes                                |            7           |            13              |           yes              |         yes           |          yes           |
|o1-preview             |Yes                                |            9           |            34              |           yes              |         yes           |          yes           |
|o3                     |Yes                                |            6           |            11              |           yes              |         yes           |          yes           |
|o3-mini                |Yes                                |            7           |             7              |           yes              |         yes           |          yes           |
|o4-mini                |Yes                                |            8           |             8              |           yes              |         yes           |          yes           |



gpt-4.1-nano provide a very specific result by defining first all the differents kinds of nodes as classes then defined Object properties like 
connects, relatesTo, bridges, partOf, hasRelation (all the relations are visible in ontograph(Protégé))

* This model provided a result file not coherent with the prompt, some comments was added by the LLM that broken the turtle format. After removing these comments the result file has been correctly processed by Protégé and ROBOTS.
