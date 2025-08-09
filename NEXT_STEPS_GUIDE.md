# HackRx 6.0 API - Next Steps Guide

## 🎯 Overview

This guide will walk you through the complete process of deploying your HackRx 6.0 API using the `venv-vertex` virtual environment.

## 📋 Prerequisites Check

### 1. Virtual Environment Setup

Your virtual environment is already set up at `venv-vertex/`. Let's verify it's working:

```bash
# Activate the virtual environment
source venv-vertex/bin/activate

# Check Python version
python --version

# Check if Groq is installed
pip list | grep groq
```

### 2. Install Missing Dependencies

If any dependencies are missing, install them:

```bash
# Activate virtual environment first
source venv-vertex/bin/activate

# Install Groq API
pip install groq==0.4.2

# Install FastAPI and other dependencies
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 pydantic==2.5.0

# Install other required packages
pip install -r requirements.txt
```

## 🚀 Step 1: Test Locally

### 1.1 Test Groq API Integration

```bash
# Activate virtual environment
source venv-vertex/bin/activate

# Test Groq integration
python test_groq.py
```

### 1.2 Test API Locally

```bash
# Activate virtual environment
source venv-vertex/bin/activate

# Run the API locally
python run_local.py
```

This will start the API at `http://localhost:8000`

### 1.3 Test API Endpoint

Open a new terminal and test the API:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test the main endpoint
curl -X POST "http://localhost:8000/hackrx/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-api-key" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": ["What is the grace period for premium payment?"]
  }'
```

## 🌐 Step 2: Deploy to Platform

### Option A: Heroku (Recommended)

#### 2.1 Install Heroku CLI

```bash
# Install Heroku CLI (if not already installed)
brew install heroku/brew/heroku

# Or download from: https://devcenter.heroku.com/articles/heroku-cli
```

#### 2.2 Create Heroku App

```bash
# Login to Heroku
heroku login

# Create a new app
heroku create your-hackrx-app-name

# Set the remote
git remote add heroku https://git.heroku.com/your-hackrx-app-name.git
```

#### 2.3 Deploy to Heroku

```bash
# Add all files
git add .

# Commit changes
git commit -m "Deploy HackRx 6.0 API with Groq integration"

# Push to Heroku
git push heroku main
```

#### 2.4 Verify Deployment

```bash
# Check app status
heroku ps

# View logs
heroku logs --tail

# Test the deployed API
curl https://your-hackrx-app-name.herokuapp.com/health
```

### Option B: Railway

#### 2.1 Connect to Railway

1. Go to [Railway](https://railway.app/)
2. Sign up/Login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Connect your repository

#### 2.2 Deploy

Railway will automatically detect your Python app and deploy it.

### Option C: Render

#### 2.1 Create Render Account

1. Go to [Render](https://render.com/)
2. Sign up/Login
3. Click "New +" → "Web Service"

#### 2.2 Configure Deployment

- **Name**: `hackrx-api`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn api:app --host=0.0.0.0 --port=$PORT`

## 🎯 Step 3: Submit to HackRx 6.0 Platform

### 3.1 Get Your Webhook URL

After deployment, your webhook URL will be:
```
https://your-app-name.herokuapp.com/hackrx/run
```

### 3.2 Submit to Platform

1. Go to the HackRx 6.0 platform
2. Navigate to "Submissions"
3. Click "Submit"
4. Enter your webhook URL
5. Add description: `FastAPI + Groq API (Llama 3 70B) + FAISS Vector Search + RAG Architecture`
6. Click "Run" to test

### 3.3 Test Submission

The platform will automatically test your API with sample questions and documents.

## 🔍 Step 4: Monitor and Debug

### 4.1 Check Logs

```bash
# Heroku logs
heroku logs --tail

# Or check the platform's dashboard
```

### 4.2 Monitor Performance

- Response times should be < 30 seconds
- Accuracy should be > 80%
- Check for any errors in logs

### 4.3 Common Issues and Solutions

#### Issue: Import Errors
```bash
# Make sure virtual environment is activated
source venv-vertex/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### Issue: Groq API Errors
- Check if API key is valid
- Ensure you have sufficient credits
- Verify the API key in `rag/query_engine.py`

#### Issue: Deployment Failures
- Check if all files are committed
- Verify `Procfile` and `runtime.txt` are present
- Check Heroku/Railway/Render logs

## 📊 Step 5: Performance Optimization

### 5.1 Monitor Response Times

```bash
# Test response time
time curl -X POST "https://your-app.herokuapp.com/hackrx/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-api-key" \
  -d '{"documents": "https://example.com/policy.pdf", "questions": ["Test question"]}'
```

### 5.2 Optimize if Needed

- Adjust `max_tokens` in Groq API call
- Optimize vector search parameters
- Consider caching for frequently asked questions

## 🎉 Success Checklist

- [ ] Virtual environment activated and working
- [ ] Local testing successful
- [ ] API deployed to cloud platform
- [ ] Webhook URL obtained
- [ ] Submitted to HackRx 6.0 platform
- [ ] Platform tests passed
- [ ] Performance monitoring set up

## 🆘 Troubleshooting

### If Virtual Environment Issues

```bash
# Recreate virtual environment
rm -rf venv-vertex
python3 -m venv venv-vertex
source venv-vertex/bin/activate
pip install -r requirements.txt
```

### If Deployment Issues

```bash
# Check if all files are tracked
git status

# Force push if needed
git push heroku main --force
```

### If API Issues

```bash
# Check logs
heroku logs --tail

# Restart the app
heroku restart
```

## 📞 Support

If you encounter issues:

1. Check the logs first
2. Verify all dependencies are installed
3. Test locally before deploying
4. Contact the development team

---

**🎯 You're Ready to Compete!**

Your HackRx 6.0 API is now deployed and ready for submission. Good luck in the competition! 🚀
