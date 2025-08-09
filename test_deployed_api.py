#!/usr/bin/env python3
"""
Test script for the deployed HackRx 6.0 API
"""

import requests
import json

# API endpoint
BASE_URL = "https://bajaj-bugfinders.onrender.com"

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_main_endpoint():
    """Test the main /hackrx/run endpoint"""
    try:
        url = f"{BASE_URL}/hackrx/run"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer test-api-key"
        }
        data = {
            "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
            "questions": [
                "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
                "What is the waiting period for pre-existing diseases (PED) to be covered?"
            ]
        }
        
        print("🧪 Testing main endpoint...")
        response = requests.post(url, json=data, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Main endpoint working!")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Main endpoint failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Main endpoint error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing deployed HackRx 6.0 API...")
    print(f"Base URL: {BASE_URL}")
    print("-" * 50)
    
    # Test health endpoint
    health_ok = test_health_endpoint()
    print()
    
    # Test main endpoint
    main_ok = test_main_endpoint()
    print()
    
    if health_ok and main_ok:
        print("🎉 All tests passed! Your API is ready for submission!")
        print(f"\n📋 Webhook URL for HackRx 6.0 platform:")
        print(f"{BASE_URL}/hackrx/run")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
