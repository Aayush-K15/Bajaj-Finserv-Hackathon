#!/usr/bin/env python3
"""
Local development server for HackRx 6.0 API
"""

import uvicorn
import os

if __name__ == "__main__":
    # Set environment variables for local development
    os.environ.setdefault("PORT", "8000")
    
    print("🚀 Starting HackRx 6.0 API locally...")
    print("📍 API will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🔍 Health check at: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server")
    
    # Run the API
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level="info"
    )
