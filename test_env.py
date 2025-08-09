
import os
from dotenv import load_dotenv

def test_env_variables():
    load_dotenv()
    
    print("Testing environment variables:")
    print("-" * 40)
    
    env_vars = [
        'PROJECT_NAME',
        'PROJECT_ID', 
        'COMPANY_NAME',
        'GCP_PROJECT_ID',
        'SERVICE_ACCOUNT_FILE',
        'CREDENTIALS_FILE',
        'TOKEN_FILE',
        'DEFAULT_TOKEN_FILE',
        'EMAIL_ATTACHMENTS_DIR',
        'UPLOADED_DOCS_DIR',
        'VECTORSTORE_DIR',
        'EMBEDDINGS_DIR',
        'VENV_DIR'
    ]
    
    for var in env_vars:
        value = os.getenv(var, 'NOT FOUND')
        print(f"{var}: {value}")
    
    print("-" * 40)
    print("Environment variables test complete!")

if __name__ == "__main__":
    test_env_variables()
