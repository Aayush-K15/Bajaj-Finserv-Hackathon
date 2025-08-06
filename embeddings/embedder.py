import os
import re
from typing import List
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("intfloat/e5-base-v2")

def split_into_chunks(text: str, max_words: int = 15000) -> List[str]:
    # Split text by double newlines or periods
    raw_chunks = re.split(r"\n\s*\n|(?<=\.)\s+", text)
    
    chunks = []
    current_chunk = []
    word_count = 0

    for section in raw_chunks:
        words = section.split()
        if word_count + len(words) > max_words:
            chunks.append(" ".join(current_chunk))
            current_chunk = words
            word_count = len(words)
        else:
            current_chunk.extend(words)
            word_count += len(words)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def get_embeddings(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []

    all_chunks = []
    for text in texts:
        all_chunks.extend(split_into_chunks(text, max_words=15000))

    embeddings = embedding_model.encode(all_chunks, convert_to_numpy=True).tolist()
    return embeddings