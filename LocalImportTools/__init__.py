import os
import sys
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import ElasticsearchStore
from langchain_community.document_loaders import TextLoader
from file_walker import find_md_files
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# secrets
ELASTIC_CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# settings
ELASTIC_INDEX = os.getenv("ELASTIC_INDEX", "embedding_test_index")
ELASTIC_NUM_DOCS = os.getenv("ELASTIC_NUM_DOCS", 5)
OPENAI_AI_EMBEDDING_MODEL = os.getenv("OPENAI_AI_EMBEDDING_MODEL", "text-embedding-ada-002")

BASE_URL = os.getenv("BASE_URL", "https://www.github.com/UKHO/docs/blob/main/")

# Embedding model used to vectorise
embeddings = OpenAIEmbeddings(openai_api_key = OPENAI_API_KEY, model = OPENAI_AI_EMBEDDING_MODEL)

db = ElasticsearchStore(
    es_cloud_id=ELASTIC_CLOUD_ID,
    index_name=ELASTIC_INDEX,
    embedding=embeddings,
    es_api_key=ELASTIC_API_KEY,
    distance_strategy="COSINE"
    # distance_strategy="EUCLIDEAN_DISTANCE"
    # distance_strategy="DOT_PRODUCT"    
)

def convert_to_url(path, basepath):
    url = f"{BASE_URL}{path[len(basepath):]}"
    head, tail = os.path.split(path)
    return f'<a href="{url}">{tail}</a>'

def index_docs_elastic(directory_path, extension):
    md_files = find_md_files(directory_path, extension)

    for file_path in md_files:
        print(file_path)

        # Load the document
        loader = TextLoader(file_path, encoding="utf-8")
        documents = loader.load()

        # Split into chunks
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        docs = text_splitter.split_documents(documents)

        # Adding metadata to documents
        for i, doc in enumerate(docs):
            doc.metadata["filename"] = convert_to_url(file_path, directory_path)

        index = db.from_documents(docs, embeddings, index_name=ELASTIC_INDEX, es_cloud_id=ELASTIC_CLOUD_ID, es_api_key = ELASTIC_API_KEY)
        print("data imported into elastic")


if (len(sys.argv) > 1):
    local_path = sys.argv[1]
    print(f"Scanning: {local_path}")

    # a second argument means skip the indexing phase
    #if (len(sys.argv) < 3):
    # read the local .md files and index into elastic
    index_docs_elastic(local_path, '.md')

    # ensure all data is refreshed
    db.client.indices.refresh(index=ELASTIC_INDEX)
    
    # try it out
    test_query = "SAST security policy"
    results = db.similarity_search(test_query, k = 4)
    print(results)
else:
    print("USEAGE: import_local_docs <path> <skip>")