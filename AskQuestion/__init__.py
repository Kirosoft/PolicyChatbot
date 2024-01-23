import logging
from azure.functions import HttpRequest, HttpResponse
from langchain_community.vectorstores import ElasticsearchStore
from .llm_integrations import get_llm
from .elasticsearch_client import elasticsearch_client
from langchain.embeddings import OpenAIEmbeddings
import os
import jinja2
from  .templates import rag_prompt

def main(req: HttpRequest) -> HttpResponse:
    INDEX = os.getenv("ES_INDEX", "workplace-app-docs")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
    ES_NUM_DOCS = os.getenv("ES_NUM_DOCS", 10)

    logging.info(f'Python HTTP trigger function processed a request.')

    question = req.params.get('question')
    if not question:
        try:
            req_body = req.get_json()
        except ValueError:
            question = "no specific question"
        else:
            question  = req_body.get('question')

    # connect to elastic and intialise a connection to the vector store
    store = ElasticsearchStore(
        es_connection=elasticsearch_client,
        index_name=INDEX,
        embedding=OpenAIEmbeddings(openai_api_key = OPENAI_API_KEY, model = EMBEDDING_MODEL)
    )

    # use the input question to do a lookup similarity search in elastic
    store.client.indices.refresh(index=INDEX)
    results = store.similarity_search(question, k = ES_NUM_DOCS)

    # transform the search results into json payload
    doc_results = []
    for doc in results:
        doc_source = {**doc.metadata, 'page_content': doc.page_content}
        doc_results.append(doc_source)
 
    # create the prompt template
    template = jinja2.Template(rag_prompt)
    qa_prompt = template.render(question=question, docs=doc_results)

    # send to the AI bot
    answer = ''
    for chunk in get_llm().stream(qa_prompt):
        answer += chunk.content


    return HttpResponse(answer)
 