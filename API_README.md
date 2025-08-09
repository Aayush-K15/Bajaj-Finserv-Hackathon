# HackRx 6.0 Insurance Document Q&A API

This is the API implementation for the HackRx 6.0 hackathon challenge. The API provides an intelligent question-answering system for insurance documents using AI and vector search.

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the API locally:**
```bash
python run_local.py
```

3. **Test the API:**
```bash
python test_api.py
```

### API Endpoints

#### Main Endpoint: `/hackrx/run`

**Method:** `POST`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <your-api-key>
```

**Request Body:**
```json
{
    "documents": "https://example.com/policy.pdf",
    "questions": [
        "What is the grace period for premium payment?",
        "What is the waiting period for pre-existing diseases?"
    ]
}
```

**Response:**
```json
{
    "answers": [
        "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
        "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered."
    ]
}
```

#### Health Check: `/health`

**Method:** `GET`

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-01-04T12:00:00Z"
}
```

## 🏗️ Architecture

The API is built with the following components:

- **FastAPI**: Modern, fast web framework for building APIs
- **Groq API (Llama 3 70B)**: High-performance AI model for natural language processing
- **FAISS**: Vector database for semantic search
- **Sentence Transformers**: For generating embeddings
- **PyPDF2/python-docx**: Document processing

## 🔧 Configuration

### Environment Variables

- `PORT`: Port number (default: 8000)
- `GROQ_API_KEY`: Groq API key (configured in code)

### Groq API Setup

1. Sign up for Groq API at https://console.groq.com
2. Get your API key
3. The API key is configured in the code (can be moved to environment variables for production)

## 📁 Project Structure

```
├── api.py                 # Main FastAPI application
├── test_api.py           # API testing script
├── run_local.py          # Local development server
├── requirements.txt      # Python dependencies
├── Procfile             # Heroku deployment
├── runtime.txt          # Python version
├── rag/                 # RAG (Retrieval-Augmented Generation) components
│   └── query_engine.py  # Question answering logic
├── loaders/             # Document loaders
│   ├── pdf_loader.py    # PDF processing
│   └── docx_loader.py   # DOCX processing
├── vectorstore/         # Vector database
│   └── store.py         # FAISS integration
└── embeddings/          # Embedding generation
    └── embedder.py      # Sentence transformers
```

## 🚀 Deployment

### Heroku

1. Create a new Heroku app
2. Set environment variables
3. Deploy using Git

```bash
heroku create your-app-name
git push heroku main
```

### Railway

1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically

### Render

1. Create new Web Service
2. Connect repository
3. Set build and start commands
4. Deploy

## 🧪 Testing

### Manual Testing

Use curl to test the API:

```bash
curl -X POST "http://localhost:8000/hackrx/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-api-key" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": ["What is the grace period for premium payment?"]
  }'
```

### Automated Testing

Run the test script:

```bash
python test_api.py
```

## 🔍 Monitoring

The API includes comprehensive logging for monitoring:

- Request/response logging
- Error tracking
- Performance metrics
- Document processing status

## 🛠️ Development

### Adding New Features

1. Fork the repository
2. Create a feature branch
3. Implement changes
4. Add tests
5. Submit pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings
- Include error handling

## 📞 Support

For issues and questions:

1. Check the logs for error messages
2. Review the API documentation at `/docs`
3. Test with the provided test script
4. Contact the development team

## 📄 License

This project is developed for the HackRx 6.0 hackathon.
