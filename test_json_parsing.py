#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.query_engine import extract_first_json, clean_json_string
import json

def test_json_parsing():
    """Test the improved JSON parsing functions"""
    
    # Test case 1: Truncated JSON (like in your error)
    truncated_json = '''
{
  "decision": "Rejected",
  "amount": "Not Applicable",
  "confidence": "High",
  "summary": "The claim is likely to be rejected because the policy has only been active for 3 months. Knee surgery, if not caused by an accident, is subject to a 24-month waiting period for both pre-existing diseases and specified procedures. Since the policyholder has not completed this waiting period, the expenses for the surgery would not be covered.",
  "justification": [
    {
      "clause": "Expenses related to the treatment of a pre-existing Disease (PED) and its direct complications shall be excluded until the expiry of 24 months of continuous coverage after the date of inception of the first policy with insurer.",
      "source": "ICIHLIP22012V012223.pdf",
      "page": 17,
      "relevance": "The policy has only been active for 3 months, which is less than the required 24-month waiting period. If the knee condition existed before the policy started, it is considered a Pre-Existing Disease (PED) and is not covered."
    },
    {
      "clause": "Expenses related to the treatment of the listed Conditions, surgeries/treatments shall be excluded until the expiry of 24 months of continuous coverage after the date of inception of the first policy with us. This exclusion shall not be applicable for claims arising due to an accident.",
      "source": "'''
    
    print("Testing truncated JSON parsing...")
    result = extract_first_json(truncated_json)
    if result:
        print("✅ Successfully parsed truncated JSON")
        print(f"Decision: {result.get('decision')}")
        print(f"Amount: {result.get('amount')}")
        print(f"Confidence: {result.get('confidence')}")
    else:
        print("❌ Failed to parse truncated JSON")
    
    # Test case 2: JSON with markdown blocks
    markdown_json = '''```json
{
  "decision": "Approved",
  "amount": "₹50000",
  "confidence": "High"
}
```'''
    
    print("\nTesting markdown-wrapped JSON...")
    cleaned = clean_json_string(markdown_json)
    try:
        result = json.loads(cleaned)
        print("✅ Successfully cleaned and parsed markdown JSON")
        print(f"Decision: {result.get('decision')}")
    except json.JSONDecodeError:
        print("❌ Failed to parse markdown JSON")
    
    # Test case 3: JSON with trailing commas
    trailing_comma_json = '''
{
  "decision": "Rejected",
  "amount": "Not Applicable",
  "confidence": "High",
}'''
    
    print("\nTesting JSON with trailing comma...")
    cleaned = clean_json_string(trailing_comma_json)
    try:
        result = json.loads(cleaned)
        print("✅ Successfully cleaned and parsed JSON with trailing comma")
        print(f"Decision: {result.get('decision')}")
    except json.JSONDecodeError:
        print("❌ Failed to parse JSON with trailing comma")

if __name__ == "__main__":
    test_json_parsing()
