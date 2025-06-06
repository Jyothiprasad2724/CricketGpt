import faiss
import pickle
import numpy as np
from langchain.embeddings import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()
embedding_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

def load_faiss_index(index_path, metadata_path):
    index = faiss.read_index(index_path)
    with open(metadata_path, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata

def search_faiss(query, index, metadata, top_k=5):
    query_vec = np.array(embedding_model.embed_query(query), dtype=np.float32).reshape(1, -1)
    faiss.normalize_L2(query_vec)
    D, I = index.search(query_vec, top_k)
    return [metadata[i] for i in I[0]]
