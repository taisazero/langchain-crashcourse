"""Load html from files, clean up, split, ingest into LanceDB."""
import logging
import os
from bs4 import BeautifulSoup
from langchain.document_loaders.recursive_url_loader import RecursiveUrlLoader
from langchain_community.embeddings.jina import JinaEmbeddings
from langchain_community.embeddings.sentence_transformer import HuggingFaceEmbeddings
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_transformers import Html2TextTransformer
import lancedb
from langchain_community.vectorstores import LanceDB
from dotenv import load_dotenv, find_dotenv
import os
import sys
import argparse
import torch

_ = load_dotenv(find_dotenv())

logger = logging.getLogger(__name__)
# set sys.stdout to have utf-8 encoding
sys.stdout.reconfigure(encoding="utf-8")
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# clear log file
open("../logs.log", "w").close()
logger.addHandler(logging.FileHandler('../logs.log', encoding='utf-8'))


def ingest_docs():
    urls = [
        "https://huggingface.co/docs/transformers",
        "https://huggingface.co/docs/peft",
        "https://huggingface.co/docs/datasets",
        "https://huggingface.co/docs/tokenizers",
        "https://huggingface.co/learn/nlp-course"
    ]

    documents = []
    # check if hf_docs folder exists and is not empty
    if os.path.exists("../hf_docs") and os.listdir("../hf_docs"):
        logger.info("hf_docs folder exists and is not empty. Skipping document ingestion.")
        from langchain_core.documents import Document
        # page metadata is the first line of the file
        documents = [Document(page_content=open(f"../hf_docs/{file}",  encoding="utf-8").read(), metadata={"source": open(f"../hf_docs/{file}",  encoding="utf-8").readline(), "title": ""}) for file in os.listdir("../hf_docs")]


        logger.info(f"Loaded documents from the directory ../hf_docs")
        return documents
    for url in urls:
        logger.info(f"Loading documents from {url}")
        loader = RecursiveUrlLoader(
            url=url,
            max_depth=6, #6, # 1,
            extractor=lambda x: BeautifulSoup(x, "lxml").text,
            prevent_outside=True,
        )
        temp_docs = loader.load()
        temp_docs = [doc for i, doc in enumerate(temp_docs) if doc not in temp_docs[:i]]
        documents += temp_docs

    html2text = Html2TextTransformer()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4_000, chunk_overlap=200)

    docs_transformed = html2text.transform_documents(documents)
    docs_transformed = text_splitter.split_documents(docs_transformed)

    # We try to return 'source' and 'title' metadata when querying vector store and
    # Weaviate will error at query time if one of the attributes is missing from a
    # retrieved document.
    for doc in docs_transformed:
        if "source" not in doc.metadata:
            doc.metadata["source"] = ""
        if "title" not in doc.metadata:
            doc.metadata["title"] = ""
    # log urls and one document
    all_dataset_urls = [doc.metadata["source"] for doc in docs_transformed]
    # remove duplicates
    all_dataset_urls = list(set(all_dataset_urls))
    main_urls_str = "\n".join(urls)
    logger.info(f"Loaded documents from these urls: {main_urls_str}")
    logger.info(f"Here is one document: {docs_transformed[3].page_content}")
    # if folder doesn't exist, create it
    if not os.path.exists("../hf_docs"):
        os.makedirs("../hf_docs")

    # dump curled urls:
    with open("../hf_docs/urls.txt", "w") as f:
        f.write("\n".join(all_dataset_urls))
        
    saved_docs = []
    # save docs as text files with url at the top
    for doc in docs_transformed:
     
        # derive filename from url webpage
        base_name = "__".join(doc.metadata["source"].replace("https://huggingface.co/","").split("/"))
        if base_name in saved_docs:
            file_name = base_name + "_chunk_" + str(saved_docs.count(base_name))
        else:
            file_name = base_name
        with open(f"../hf_docs/{file_name}.txt", "w", encoding="utf-8") as f:
            f.write(doc.metadata["source"] + "\n")
            f.write(doc.page_content)
            saved_docs.append(base_name)

    # log a report of how many docs were saved and how many urls were crawled
    logger.info(f"Saved {len(saved_docs)} documents to ../hf_docs")
    logger.info(f"Crawled {len(all_dataset_urls)} urls")
    return docs_transformed

def ingest_vectors(docs_transformed, model_name):
    if model_name == "openai":
        embeddings = OpenAIEmbeddings(chunk_size = 4000)
    else:
        torch.cuda.set_per_process_memory_fraction(0.9, device=0)
        encode_kwargs = {"batch_size": 1}
        model_kwargs = {'trust_remote_code' : True}
        embeddings = HuggingFaceEmbeddings(model_name= model_name, encode_kwargs = encode_kwargs,
                                            show_progress = True, multi_process = False, model_kwargs = model_kwargs)
    
    model_base_name = model_name.split("/")[1]
    db = lancedb.connect(f'../notebooks/.lancedb_hf_{model_base_name}')    
    table = db.create_table("hf_docs", data=[
    {"vector": embeddings.embed_query("Hello World"), "text": "Hello World", "id": "1"}
        ], mode="overwrite")
    docsearch = LanceDB.from_documents(docs_transformed, embeddings, connection=table)
    # log total number of documents and vector store size
    logger.info(f"Total number of documents: {len(docs_transformed)}")
    logger.info(f"Vector store size: {table.to_pandas().shape[0]}")
    
    logger.info(f"Vector store columns: {table.to_pandas().columns}")
    # instructions to load the vector database again
    logger.info(f"Run this to load the vector database again: " \
                "import lancedb\n" \
                "from langchain.vectorstores import LanceDB\n" \
                "db = lancedb.connect('/.lancedb')\n" \
                f"table = db.open_table('hf_docs')\n" \
                f"embedding_fn = HuggingFaceEmbeddings(model_name= {model_name})\n"
                f"vectorstore = LanceDB(table, embedding_fn)\n" \
            )

if __name__ == "__main__":
    instructions = """
        To run me from the command line:
        python hf_ingest_st.py
    """
    # add argument for embedding model
    parser = argparse.ArgumentParser(description="Ingest documents and vectors into LanceDB")
    parser.add_argument("--model", type=str, help="HuggingFace embedding model name or specify openai")
    args = parser.parse_args()
    if args.model:
        model_name = args.model 
    else:
        model_name = "jinaai/jina-embeddings-v2-small-en"
    print("Ingesting documents...")
    try:
        docs = ingest_docs()
        print("Ingesting vectors...")
        ingest_vectors(docs, model_name)
    except Exception as e:
        logger.error(e)
        logger.error(instructions)
        raise e