from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
import os
from uuid import uuid4

'''
This script is used to initialize the Chroma database with the references data.
Please ensure that the ground truth references are stored in the references folder.

This script is run once before the pipeline_extraction.py script is run.

command to run this script from current directory is : 
    python init_chroma.py

You can specify a collection name in the collection_name variable.
Ensure any changes to names are reflected in the pipeline_extraction.py script.
'''

files = os.listdir(os.getcwd(), "references")
references = []
collection_name = "collection_name"

for file in files:
    with open(f"references/{file}", "r", encoding="utf-8") as f:
        references.append(f.read())


all_splits = []
for reference in references:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=50)
    all_splits.extend(text_splitter.split_text(reference))

embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

persistent_client = chromadb.PersistentClient()
collection = persistent_client.get_or_create_collection(collection_name)
vector_store_from_client = Chroma(
    client=persistent_client,
    collection_name=collection_name,
    embedding_function=embeddings,
)
collection.add(documents=all_splits, ids=[str(uuid4()) for _ in range(len(all_splits))])

