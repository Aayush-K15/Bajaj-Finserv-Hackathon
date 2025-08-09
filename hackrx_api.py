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
import groq

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
        if "loaders" not in sys.modules:
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
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

def answer_questions_optimized(questions: List[str], document_chunks: List[Dict]) -> List[str]:
    """
    Optimized question answering function for speed
    """
    answers = []
    
    try:
        # Initialize Groq client
        groq_api_key = "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"
        client = groq.Groq(api_key=groq_api_key)
        
        # Create combined context from all chunks (faster than vector search)
        context_text = "\n\n---\n\n".join(
            f"Source: {chunk.get('metadata', {}).get('source', 'document')}, Page: {chunk.get('metadata', {}).get('page', '?')}\nContent:\n{chunk.get('content', '')}"
            for chunk in document_chunks[:15]  # Limit to prevent token overflow
        )
        
        for question in questions:
            try:
                # Create optimized prompt for direct answer
                prompt = f"""You are an insurance policy expert. Based on the provided policy document, answer this question clearly and concisely.

Question: {question}

Policy Document Context:
{context_text[:15000]}

Provide a direct, accurate answer based only on the information in the policy document. If the information is not available in the document, say so clearly."""
                
                # Use Groq for faster response
                response = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert insurance policy analyst. Provide clear, accurate answers based only on the provided policy document."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    model="llama3-8b-8192",  # Use faster 8B model for speed
                    temperature=0.1,
                    max_tokens=500,  # Shorter responses for speed
                    top_p=0.9
                )
                
                answer = response.choices[0].message.content.strip()
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
            
            # Answer the questions with optimized method
            answers = answer_questions_optimized(request.questions, document_chunks)
            
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
        "hackrx_api:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
