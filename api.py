import os
import json
import requests
import tempfile
import sys
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HackRx 6.0 Insurance Document Q&A API",
    description="AI-powered insurance document question answering system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QuestionRequest(BaseModel):
    documents: str
    questions: List[str]

class QuestionResponse(BaseModel):
    answers: List[str]

# Authentication function
async def verify_api_key(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    api_key = authorization.replace("Bearer ", "")
    
    # For demo purposes, accept any non-empty API key
    # In production, you would validate against a database or environment variable
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key

def download_document(url: str) -> str:
    """
    Download document from URL and return the local file path
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        
        logger.info(f"Downloaded document to {temp_file_path}")
        return temp_file_path
    
    except Exception as e:
        logger.error(f"Failed to download document from {url}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to download document: {str(e)}")

def process_document(file_path: str) -> List[Dict]:
    """
    Process document and return chunks
    """
    try:
        # Import here to avoid circular imports
        from loaders.pdf_loader import load_pdf
        from loaders.docx_loader import load_docx
        
        if file_path.lower().endswith('.pdf'):
            chunks = load_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            chunks = load_docx(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Only PDF and DOCX are supported.")
        
        logger.info(f"Processed {len(chunks)} chunks from document")
        return chunks
    
    except Exception as e:
        logger.error(f"Failed to process document {file_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

def answer_questions(questions: List[str], document_chunks: List[Dict]) -> List[str]:
    """
    Answer questions using the document chunks
    """
    answers = []
    
    try:
        # Import here to avoid circular imports
        from rag.query_engine import answer_query
        from vectorstore.store import add_to_index, save_index, load_index
        
        # Add document chunks to vector store
        if document_chunks:
            add_to_index(document_chunks)
            save_index()
            load_index()
        
        for question in questions:
            try:
                # Use the existing answer_query function
                result = answer_query(question)
                
                # Extract the direct answer
                if "direct_answer" in result and result["direct_answer"]:
                    answer = result["direct_answer"]
                elif "summary" in result and result["summary"]:
                    answer = result["summary"]
                elif "error" in result:
                    answer = f"Error: {result['error']}"
                else:
                    answer = "Unable to find a specific answer to this question based on the provided document."
                
                answers.append(answer)
                logger.info(f"Answered question: {question[:50]}...")
                
            except Exception as e:
                logger.error(f"Failed to answer question '{question}': {str(e)}")
                answers.append(f"Error processing question: {str(e)}")
    
    except Exception as e:
        logger.error(f"Failed to process questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process questions: {str(e)}")
    
    return answers

@app.get("/")
async def root():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "message": "HackRx 6.0 Insurance Document Q&A API",
        "version": "1.0.0"
    }

@app.post("/hackrx/run", response_model=QuestionResponse)
async def run_questions(
    request: QuestionRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Main endpoint for processing documents and answering questions
    """
    try:
        logger.info(f"Received request with {len(request.questions)} questions")
        
        # Download the document
        document_path = download_document(request.documents)
        
        try:
            # Process the document
            document_chunks = process_document(document_path)
            
            # Answer the questions
            answers = answer_questions(request.questions, document_chunks)
            
            # Clean up temporary file
            if os.path.exists(document_path):
                os.unlink(document_path)
            
            logger.info(f"Successfully processed {len(answers)} answers")
            
            return QuestionResponse(answers=answers)
        
        except Exception as e:
            # Clean up temporary file in case of error
            if os.path.exists(document_path):
                os.unlink(document_path)
            raise e
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in /hackrx/run: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Health check endpoint for deployment monitoring
    """
    return {
        "status": "healthy",
        "timestamp": "2025-01-04T12:00:00Z"
    }

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
