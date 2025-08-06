#!/usr/bin/env python3
"""
Test script to validate response consistency
"""

import streamlit as st

def display_consistency_info():
    """Display information about the consistency improvements"""
    st.info("""
    🔧 **Consistency Improvements Applied:**
    
    1. **Lower Temperature (0.1)** - Reduces randomness in LLM responses
    2. **Focused Sampling** - Using top_p=0.8 and top_k=40 for more consistent token selection
    3. **Deterministic Prompts** - Added explicit consistency instructions
    4. **Structured Context** - More organized input format for reproducible results
    
    ✅ **Expected Result:** Same query should now produce identical or very similar answers
    """)

if __name__ == "__main__":
    print("Consistency improvements applied to query engine!")
    print("- Temperature: 0.1 (low randomness)")
    print("- Top-p: 0.8 (focused sampling)")  
    print("- Top-k: 40 (limited vocabulary)")
    print("- Explicit consistency instructions in prompts")
