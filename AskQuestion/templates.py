rag_prompt = '''
Use the following passages to answer the user's question. 
Each passage has a NAME which is the title of the document. After your answer, leave a blank line and then give the source name of the passages you answered from. Put them in a comma separated list, prefixed with SOURCES:.

Example:

Question: What is the meaning of life?
Response:
The meaning of life is 42.

SOURCES: Hitchhiker's Guide to the Galaxy

If you don't know the answer, just say that you don't know, don't try to make up an answer.

----

{% for doc in docs -%}
---
NAME: {{ doc.filename }}
PASSAGE:
{{ doc.page_content }}
---

{% endfor -%}
----
Question: {{ question }}
Response:
'''

