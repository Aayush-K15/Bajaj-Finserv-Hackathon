

import os
import extract_msg
from typing import List, Dict

def load_msg(file_path: str) -> List[Dict]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    msg = extract_msg.Message(file_path)
    msg_subject = msg.subject or ""
    msg_body = msg.body or ""

    content = f"Subject: {msg_subject}\n\n{msg_body}".strip()

    return [{
        "content": content,
        "metadata": {
            "source": os.path.basename(file_path)
        }
    }]