import os
from typing import List, Dict
from docx import Document

def load_docx(file_path: str) -> List[Dict]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    doc = Document(file_path)
    full_text = []

    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(para.text.strip())

    content = "\n".join(full_text)

    return [{
        "content": content,
        "metadata": {
            "source": os.path.basename(file_path)
        }
    }]
