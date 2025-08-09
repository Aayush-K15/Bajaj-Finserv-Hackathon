#!/bin/bash

# HackRx 6.0 API Setup and Deployment Script
# This script will help you set up and deploy your API

echo "🚀 HackRx 6.0 API Setup and Deployment Script"
echo "=============================================="

# Check if virtual environment exists
if [ ! -d "venv-vertex" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv-vertex
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv-vertex/bin/activate

# Check Python version
echo "🐍 Python version:"
python --version

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if Groq is installed
if ! pip show groq > /dev/null 2>&1; then
    echo "⚠️  Groq not found. Installing..."
    pip install groq==0.4.2
fi

# Check if FastAPI is installed
if ! pip show fastapi > /dev/null 2>&1; then
    echo "⚠️  FastAPI not found. Installing..."
    pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 pydantic==2.5.0
fi

echo "✅ Dependencies installed successfully!"

# Test Groq integration
echo "🧪 Testing Groq integration..."
python test_groq.py

if [ $? -eq 0 ]; then
    echo "✅ Groq integration test passed!"
else
    echo "⚠️  Groq integration test failed. Check the error above."
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Test locally: python run_local.py"
echo "2. Deploy to Heroku:"
echo "   - heroku create your-app-name"
echo "   - git add . && git commit -m 'Deploy API'"
echo "   - git push heroku main"
echo "3. Submit to HackRx 6.0 platform with your webhook URL"
echo ""
echo "📚 For detailed instructions, see: NEXT_STEPS_GUIDE.md"
echo ""
echo "🎉 Setup complete! Good luck with your submission!"
