# PolicyChatbot

# Retrieval Augmented Generation - Policy Chat bot

This application is designed to provide an AI chatbot interface with any text document sources.

## Tech Stack:

OpenAI ChatGPT4 as the LLM Model
ElasticSearchCloud as the vectorstore
Azure functions to run the chatgpt as a functional lambda

Step 1. Download the document you want to 'chat with to local drive
Step 2: Run the 'LocalImportTools' to scan the locally downloaded documents. For example:
'''
# activate the local env (windows)
.venv\Scripts\activate

# create your .env file in the project root
ELASTIC_CLOUD_ID = "YourElasticCloudId"
ELASTIC_API_KEY = "YourElasticCloudAPIKey"
ELASTIC_INDEX = "embedding_test_index"
ELASTIC_NUM_DOCS = "15"
OPENAI_API_KEY = "<YourOPenAIKey>"
OPENAI_AI_EMBEDDING_MODEL = "text-embedding-ada-002"

# run the import tool
# currently setup to import all *.md files into Elastic
# where f:\Elastic\docs is the location of your documents
& F:/Python312/python.exe f:/elastic/PolicyChatbot/LocalImportTools/__init__.py F:\elastic\docs

# Create the 'AskAQuestion' azure function
'''

Either run the azure function locally using the local Azure tools or deploy to Azure.

.venv\Scripts\activate ; func host start 

The function can be executed an takes the question as input in the http body:

AskQuestion: [GET,POST] http://localhost:7071/api/AskQuestion

body:

{ "question": "What is policy on pull requests" }
