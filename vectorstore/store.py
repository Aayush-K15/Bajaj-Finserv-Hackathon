import os
import faiss
import pickle
import numpy as np
from typing import List, Dict
from dotenv import load_dotenv
from embeddings.embedder import get_embeddings

load_dotenv()

VECTORSTORE_DIR = os.getenv('VECTORSTORE_DIR', 'vectorstore')
INDEX_PATH = os.path.join(VECTORSTORE_DIR, "index.faiss")
STORE_PATH = os.path.join(VECTORSTORE_DIR, "store.pkl")

index = None
metadata_store = []

def add_to_index(chunks: List[Dict]):
    global index, metadata_store

    texts = [chunk["content"] for chunk in chunks]
    embeddings = get_embeddings(texts)

    dim = len(embeddings[0])
    
    if index is None:
        index = faiss.IndexFlatL2(dim)
    
    index.add(np.array(embeddings).astype('float32'))
    metadata_store.extend(chunks)

def search(query: str, top_k: int = 5) -> List[Dict]:
    global index, metadata_store

    if index is None:
        raise ValueError("Index not loaded or built yet.")

    embedding = get_embeddings([query])[0]
    D, I = index.search(np.array([embedding]).astype('float32'), top_k)

    results = []
    for idx in I[0]:
        if idx < len(metadata_store):
            results.append(metadata_store[idx])
    return results

def save_index():
    global index, metadata_store
    if index is not None:
        faiss.write_index(index, INDEX_PATH)
        with open(STORE_PATH, "wb") as f:
            pickle.dump(metadata_store, f)

def load_index():
    global index, metadata_store
    if os.path.exists(INDEX_PATH) and os.path.exists(STORE_PATH):
        index = faiss.read_index(INDEX_PATH)
        with open(STORE_PATH, "rb") as f:
            metadata_store = pickle.load(f)
    else:
        raise FileNotFoundError("Index or metadata store not found.")