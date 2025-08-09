# HackRx 6.0 API Deployment Guide

This guide will help you deploy the HackRx 6.0 Insurance Document Q&A API to various platforms.

## Prerequisites

1. Python 3.11+
2. All dependencies installed (see requirements.txt)
3. Groq API key configured

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the API locally:
```bash
python api.py
```

3. Test the API:
```bash
python test_api.py
```

## Deployment Options

### 1. Heroku

1. Create a new Heroku app:
```bash
heroku create your-app-name
```

2. Deploy:
```bash
git add .
git commit -m "Deploy HackRx 6.0 API"
git push heroku main
```

### 2. Railway

1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Python app
3. Deploy automatically on push

### 3. Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn api:app --host=0.0.0.0 --port=$PORT`
5. Deploy

### 4. Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

## API Endpoints

### Main Endpoint
- **URL**: `POST /hackrx/run`
- **Authentication**: Bearer token required
- **Request Body**:
```json
{
    "documents": "https://example.com/policy.pdf",
    "questions": ["Question 1", "Question 2"]
}
```
- **Response**:
```json
{
    "answers": ["Answer 1", "Answer 2"]
}
```

### Health Check
- **URL**: `GET /health`
- **Response**: Health status

## Environment Variables

- `PORT`: Port number (default: 8000)
- `GROQ_API_KEY`: Groq API key (configured in code)

## Testing

Use the provided test script:
```bash
python test_api.py
```

Or test manually with curl:
```bash
curl -X POST "https://your-app.herokuapp.com/hackrx/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": ["What is the grace period for premium payment?"]
  }'
```

## Troubleshooting

1. **Import errors**: Make sure all dependencies are installed
2. **Groq API issues**: Ensure API key is valid and has sufficient credits
3. **Memory issues**: Consider upgrading to a larger instance on cloud platforms
4. **Timeout issues**: Increase timeout settings for document processing

## Support

For issues related to:
- API functionality: Check logs and error messages
- Deployment: Refer to platform-specific documentation
- HackRx 6.0: Contact the organizing team
