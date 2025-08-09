#!/usr/bin/env python3
"""
Quick test for the deployed API
"""

import requests

# Test health endpoint
try:
    response = requests.get("https://bajaj-bugfinders.onrender.com/health", timeout=10)
    if response.status_code == 200:
        print("✅ API is deployed and working!")
        print(f"Health check response: {response.json()}")
        print(f"\n🎯 Your webhook URL for HackRx 6.0:")
        print("https://bajaj-bugfinders.onrender.com/hackrx/run")
        print("\n🚀 Ready for submission!")
    else:
        print(f"❌ Health check failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*50)
print("📋 SUBMISSION READY!")
print("="*50)
print("1. Go to HackRx 6.0 platform")
print("2. Navigate to Submissions")
print("3. Enter webhook URL: https://bajaj-bugfinders.onrender.com/hackrx/run")
print("4. Add description: FastAPI + Groq API (Llama 3 70B) + FAISS Vector Search + RAG Architecture")
print("5. Click 'Run' to test")
print("6. Submit your solution!")
print("="*50)
