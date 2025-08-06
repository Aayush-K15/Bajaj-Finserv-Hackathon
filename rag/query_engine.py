


import os
import re
import json
from typing import Dict, List, Any
from vectorstore import store
from vertexai.preview.generative_models import GenerativeModel
import vertexai

# Initialize Vertex AI
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "bajaj-finserv-hackathon-468017-5c524f36fc39.json"
vertexai.init(
    project="bajaj-finserv-hackathon-468017",
    location="us-central1" 
)

model = GenerativeModel("gemini-2.5-flash")

def parse_query_structure(query: str) -> Dict[str, Any]:
    """
    Parse and structure the query to identify key details such as age, procedure, location, and policy duration.
    """
    structured_query = {
        "original_query": query,
        "age": None,
        "gender": None,
        "procedure": None,
        "location": None,
        "policy_duration": None,
        "amount": None,
        "other_details": []
    }
    
    query_lower = query.lower()
    
    # Extract age (e.g., "46M", "32F", "25 years old", "45-year-old")
    age_patterns = [
        r'(\d+)(?:m|f|male|female)',  # 46M, 32F
        r'(\d+)\s*(?:years?\s*old|yr|yrs)',  # 25 years old, 30 yr
        r'(\d+)[-\s]*year[-\s]*old',  # 45-year-old
        r'age\s*:?\s*(\d+)',  # age: 30
        r'(\d+)\s*(?:male|female)',  # 46 male
    ]
    
    for pattern in age_patterns:
        match = re.search(pattern, query_lower)
        if match:
            structured_query["age"] = int(match.group(1))
            break
    
    # Extract gender
    if re.search(r'\b(\d+)m\b', query_lower) or re.search(r'\bmale\b', query_lower):
        structured_query["gender"] = "male"
    elif re.search(r'\b(\d+)f\b', query_lower) or re.search(r'\bfemale\b', query_lower):
        structured_query["gender"] = "female"
    
    # Extract procedure/treatment/surgery
    procedure_keywords = [
        'surgery', 'operation', 'procedure', 'treatment', 'therapy',
        'knee', 'hip', 'heart', 'cardiac', 'bypass', 'transplant',
        'hospitalization', 'admission', 'consultation', 'diagnostic',
        'mri', 'ct scan', 'x-ray', 'blood test', 'biopsy'
    ]
    
    procedures_found = []
    for keyword in procedure_keywords:
        if keyword in query_lower:
            procedures_found.append(keyword)
    
    if procedures_found:
        structured_query["procedure"] = procedures_found
    
    # Extract location/city
    location_patterns = [
        r'\b(mumbai|delhi|bangalore|chennai|kolkata|pune|hyderabad|ahmedabad|surat|jaipur)\b',
        r'\bin\s+([a-zA-Z]+)',  # "in Pune", "in Delhi"
        r'\bat\s+([a-zA-Z]+)',  # "at Mumbai"
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, query_lower)
        if match:
            structured_query["location"] = match.group(1).title()
            break
    
    # Extract policy duration
    duration_patterns = [
        r'(\d+)[-\s]*(?:month|months?)\s*policy',  # 3-month policy
        r'(\d+)[-\s]*(?:year|years?)\s*policy',   # 2-year policy
        r'policy\s*(?:of|for)\s*(\d+)\s*(?:month|year)',  # policy of 6 months
    ]
    
    for pattern in duration_patterns:
        match = re.search(pattern, query_lower)
        if match:
            duration_value = int(match.group(1))
            duration_unit = "months" if "month" in match.group(0) else "years"
            structured_query["policy_duration"] = f"{duration_value} {duration_unit}"
            break
    
    # Extract amounts
    amount_patterns = [
        r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)',  # ₹50,000
        r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)',  # Rs. 50000
        r'rupees\s*(\d+(?:,\d+)*(?:\.\d+)?)',  # rupees 50000
        r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:rupees|rs)',  # 50000 rupees
    ]
    
    for pattern in amount_patterns:
        match = re.search(pattern, query_lower)
        if match:
            amount_str = match.group(1).replace(',', '')
            structured_query["amount"] = float(amount_str)
            break
    
    return structured_query

def enhance_search_query(structured_query: Dict[str, Any]) -> str:
    """
    Enhance the search query for better semantic retrieval.
    """
    enhanced_terms = [structured_query["original_query"]]
    
    # Add relevant search terms based on structured data
    if structured_query["procedure"]:
        procedures = structured_query["procedure"]
        enhanced_terms.extend(procedures)
        
        # Add related medical terms
        medical_terms = {
            'knee': ['orthopedic', 'joint replacement', 'arthroscopy', 'ligament'],
            'heart': ['cardiac', 'cardiovascular', 'coronary', 'bypass'],
            'surgery': ['surgical procedure', 'operation', 'medical treatment'],
            'hospitalization': ['inpatient', 'admission', 'hospital stay']
        }
        
        for proc in procedures:
            if proc in medical_terms:
                enhanced_terms.extend(medical_terms[proc])
    
    # Add age-related terms
    if structured_query["age"]:
        age = structured_query["age"]
        if age >= 60:
            enhanced_terms.extend(['senior citizen', 'elderly', 'age limit'])
        elif age < 18:
            enhanced_terms.extend(['minor', 'child', 'pediatric'])
    
    # Add policy duration terms
    if structured_query["policy_duration"]:
        enhanced_terms.extend(['waiting period', 'policy term', 'coverage period'])
    
    # Add coverage and claim related terms
    enhanced_terms.extend([
        'coverage', 'covered', 'eligible', 'claim', 'benefit',
        'exclusion', 'limitation', 'pre-existing', 'waiting period'
    ])
    
    return " ".join(enhanced_terms)

def format_prompt(query: str, context_chunks: list, structured_query: dict = None) -> str:
    """
    Enhanced prompt formatting with structured query analysis.
    """
    context_text = "\n\n---\n\n".join(
        f"Source: {chunk['metadata']['source']}, Page: {chunk['metadata'].get('page', '?')}\nContent:\n{chunk['content']}"
        for chunk in context_chunks
    )
    
    # Include structured query information if available
    structured_info = ""
    if structured_query:
        structured_info = f"""
PARSED QUERY DETAILS:
- Age: {structured_query.get('age', 'Not specified')}
- Gender: {structured_query.get('gender', 'Not specified')}
- Procedure: {', '.join(structured_query.get('procedure', [])) if structured_query.get('procedure') else 'Not specified'}
- Location: {structured_query.get('location', 'Not specified')}
- Policy Duration: {structured_query.get('policy_duration', 'Not specified')}
- Amount: {structured_query.get('amount', 'Not specified')}

"""
    
    prompt = f"""
You are an insurance policy assistant with expertise in claims processing and policy interpretation.

{structured_info}ORIGINAL USER QUERY:
"{query}"

RELEVANT POLICY CLAUSES AND DOCUMENTS:
{context_text}

INSTRUCTIONS:
1. First, provide a clear, direct answer to the user's question in one simple sentence
2. Then provide the detailed JSON response for analysis

Format your response exactly like this:

ANSWER: [Your direct answer here - e.g., "Yes, knee surgery is covered under the policy." or "No, this procedure is not covered."]

JSON:
{{
  "decision": "Approved" or "Rejected",
  "amount": "₹Amount if applicable, else Not Applicable",
  "confidence": "High/Medium/Low based on available information",
  "summary": "Brief explanation of the decision",
  "justification": [
    {{
      "clause": "exact text of the clause that supports your decision",
      "source": "filename.pdf",
      "page": 14,
      "relevance": "how this clause applies to the specific query"
    }}
  ],
  "additional_requirements": [
    "Any additional documents or steps needed"
  ],
  "exclusions_checked": [
    "List of exclusions that were evaluated"
  ]
}}
"""
    return prompt.strip()

def answer_query(query: str, context: str = None) -> dict:
    """
    Enhanced query processing with structured analysis and semantic understanding.
    """
    # Parse and structure the query
    structured_query = parse_query_structure(query)
    
    if context:
        # Use provided context directly (for email/attachment content)
        prompt = f"""
You are an insurance policy assistant with expertise in claims processing and policy interpretation.

PARSED QUERY DETAILS:
- Age: {structured_query.get('age', 'Not specified')}
- Gender: {structured_query.get('gender', 'Not specified')}
- Procedure: {', '.join(structured_query.get('procedure', [])) if structured_query.get('procedure') else 'Not specified'}
- Location: {structured_query.get('location', 'Not specified')}
- Policy Duration: {structured_query.get('policy_duration', 'Not specified')}
- Amount: {structured_query.get('amount', 'Not specified')}

ORIGINAL USER QUERY:
"{query}"

CONTEXT FROM EMAIL AND ATTACHMENTS:
{context}

INSTRUCTIONS:
1. First, provide a clear, direct answer to the user's question in one simple sentence
2. Then provide the detailed JSON response for analysis

Format your response exactly like this:

ANSWER: [Your direct answer here - e.g., "Yes, knee surgery is covered under the policy." or "No, this procedure is not covered."]

JSON:
{{
  "decision": "Approved" or "Rejected" or "Partial" or "Information",
  "amount": "₹Amount if applicable, else null",
  "confidence": "High/Medium/Low based on available information",
  "summary": "Brief explanation of the decision",
  "justification": [
    {{
      "clause": "text from the context that supports your answer",
      "source": "email/attachment",
      "page": "N/A",
      "relevance": "how this information applies to the query"
    }}
  ],
  "additional_requirements": [
    "Any additional documents or steps needed"
  ],
  "query_interpretation": {{
    "understood_as": "How the system interpreted the query",
    "assumptions_made": ["Any assumptions made for incomplete information"]
  }}
}}
"""
    else:
        # Use enhanced semantic search with vector store
        try:
            store.load_index()
            
            # Enhance search query for better retrieval
            enhanced_query = enhance_search_query(structured_query)
            
            # Search with enhanced query and get more results for better coverage
            top_chunks = store.search(enhanced_query, top_k=8)
            
            # Also search with original query to ensure we don't miss anything
            original_chunks = store.search(query, top_k=5)
            
            # Combine and deduplicate chunks
            all_chunks = top_chunks + original_chunks
            seen_content = set()
            unique_chunks = []
            for chunk in all_chunks:
                content_key = chunk['content'][:100]  # Use first 100 chars as key
                if content_key not in seen_content:
                    seen_content.add(content_key)
                    unique_chunks.append(chunk)
            
            # Limit to top 10 most relevant chunks
            final_chunks = unique_chunks[:10]
            
            prompt = format_prompt(query, final_chunks, structured_query)
            
        except Exception as e:
            return {
                "error": "Vector store search failed",
                "details": str(e),
                "structured_query": structured_query
            }

    # Generate response using Gemini
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Parse the response to extract ANSWER and JSON parts
        if "ANSWER:" in response_text and "JSON:" in response_text:
            # Split the response
            parts = response_text.split("JSON:", 1)
            direct_answer = parts[0].replace("ANSWER:", "").strip()
            json_part = parts[1].strip()
            
            # Clean JSON part
            if json_part.startswith("```json"):
                json_part = json_part[7:]
            if json_part.startswith("```"):
                json_part = json_part[3:]
            if json_part.endswith("```"):
                json_part = json_part[:-3]
            json_part = json_part.strip()
            
            # Parse JSON
            try:
                result = json.loads(json_part)
                result["direct_answer"] = direct_answer
            except json.JSONDecodeError:
                result = {
                    "direct_answer": direct_answer,
                    "error": "Failed to parse JSON part",
                    "raw_json": json_part
                }
        else:
            # Fallback to old parsing method
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                result = json.loads(response_text)
                result["direct_answer"] = "Please check the detailed analysis below."
            except json.JSONDecodeError:
                result = {
                    "direct_answer": "Unable to process the response.",
                    "error": "Failed to parse response",
                    "raw": response.text
                }
        
        # Add metadata about query processing
        result["_metadata"] = {
            "structured_query": structured_query,
            "enhanced_search": not bool(context),
            "chunks_used": len(final_chunks) if not context else "direct_context"
        }
        
    except Exception as e:
        result = {
            "direct_answer": "An error occurred while processing your query.",
            "error": "Failed to generate or parse response", 
            "exception": str(e),
            "structured_query": structured_query
        }
    
    return result