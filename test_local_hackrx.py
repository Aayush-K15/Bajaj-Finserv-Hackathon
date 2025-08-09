import requests
import json
import time

# Test the optimized API locally first
url = "http://localhost:8000/hackrx/run"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer test-api-key"
}

# Use a simple test case first
payload = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under this policy?"
    ]
}

print("Testing optimized HackRx API...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

start_time = time.time()

try:
    response = requests.post(url, headers=headers, json=payload, timeout=120)
    end_time = time.time()
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Time: {end_time - start_time:.2f} seconds")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("\n✅ API is working correctly!")
        
        # Now test with multiple questions
        payload_multi = {
            "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
            "questions": [
                "What is the grace period for premium payment?",
                "What is the waiting period for pre-existing diseases?",
                "Does this policy cover maternity expenses?"
            ]
        }
        
        print("\n🔄 Testing with multiple questions...")
        start_time = time.time()
        response_multi = requests.post(url, headers=headers, json=payload_multi, timeout=120)
        end_time = time.time()
        
        print(f"Status Code: {response_multi.status_code}")
        print(f"Response Time: {end_time - start_time:.2f} seconds")
        print(f"Number of answers: {len(response_multi.json().get('answers', []))}")
        
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Request failed: {e}")

print("\nTo run the optimized server:")
print("python hackrx_api.py")
