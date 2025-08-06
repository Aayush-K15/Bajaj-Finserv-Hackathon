

import os
from typing import List, Dict
from PyPDF2 import PdfReader

def load_pdf(file_path: str) -> List[Dict]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    reader = PdfReader(file_path)
    document_chunks = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            document_chunks.append({
                "content": text.strip(),
                "metadata": {
                    "source": os.path.basename(file_path),
                    "page": i + 1
                }
            })
    
    return document_chunks