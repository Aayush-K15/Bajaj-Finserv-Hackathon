#!/usr/bin/env python3
"""
Test script for Groq API integration
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_groq_integration():
    """Test Groq API integration"""
    try:
        # Import the query engine
        from rag.query_engine import answer_query
        
        print("✅ Successfully imported query_engine with Groq")
        
        # Test a simple query
        test_query = "What is the grace period for premium payment?"
        test_context = "The policy provides a grace period of thirty days for premium payment after the due date."
        
        print(f"Testing query: {test_query}")
        result = answer_query(test_query, context=test_context)
        
        if "error" in result:
            print(f"❌ Error in Groq API: {result['error']}")
            return False
        else:
            print("✅ Groq API integration successful!")
            print(f"Response: {result.get('direct_answer', 'No direct answer')}")
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing Groq integration: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Groq API integration...")
    success = test_groq_integration()
    if success:
        print("🎉 All tests passed!")
    else:
        print("💥 Tests failed!")
        sys.exit(1)
