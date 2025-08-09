import requests
import json

# Test your API with the exact HackRx format
url = "https://bajaj-bugfinders.onrender.com/hackrx/run"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer test-api-key"
}

# Use their exact test format
payload = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?"
    ]
}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ API is working correctly!")
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Request failed: {e}")
