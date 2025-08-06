import os
import base64
import streamlit as st

from loaders.pdf_loader import load_pdf
from loaders.docx_loader import load_docx

def extract_text_from_file(uploaded_file, file_path):
    """
    Extract text from uploaded file using the correct file path.
    """
    filename = uploaded_file.name.lower()
    if filename.endswith(".pdf"):
        chunks = load_pdf(file_path)  # Use the full file path
    elif filename.endswith(".docx"):
        chunks = load_docx(file_path)  # Use the full file path
    else:
        return "Unsupported file format."

    return "\n\n".join(chunk["content"] for chunk in chunks if "content" in chunk)

ATTACHMENTS_DIR = "email_attachments"
os.makedirs(ATTACHMENTS_DIR, exist_ok=True)

from rag.query_engine import answer_query
from gmail_reader import authenticate_gmail, get_matching_emails, get_email_body, save_attachment
from vectorstore.store import add_to_index, search, save_index, load_index
def format_definitive_answer(result: dict, query: str) -> str:
    """
    Display the direct answer from the LLM response.
    """
    if "error" in result:
        return "❌ Unable to process your query due to an error. Please try again."
    
    # Use the direct answer from the LLM if available
    if "direct_answer" in result and result["direct_answer"]:
        answer = result["direct_answer"]
        
        # Add confidence indicator if available
        confidence = result.get("confidence", "Medium")
        confidence_emoji = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}.get(confidence, "⚪")
        answer += f" {confidence_emoji} (Confidence: {confidence})"
        
        return answer
    
    # Fallback to old method if direct_answer is not available
    decision = result.get("decision", "Unknown")
    summary = result.get("summary", "")
    confidence = result.get("confidence", "Medium")
    amount = result.get("amount")
    
    # Create definitive answer based on decision
    if decision.lower() == "approved":
        if amount and amount != "null":
            answer = f"✅ **Yes, your query is approved.** {summary} Amount: {amount}"
        else:
            answer = f"✅ **Yes, your query is approved.** {summary}"
    elif decision.lower() == "rejected":
        answer = f"❌ **No, your query is rejected.** {summary}"
    elif decision.lower() == "partial":
        if amount and amount != "null":
            answer = f"⚠️ **Partially covered.** {summary} Amount: {amount}"
        else:
            answer = f"⚠️ **Partially covered.** {summary}"
    elif decision.lower() == "information":
        answer = f"ℹ️ **Information:** {summary}"
    else:
        answer = f"📝 **Response:** {summary or 'Please review the detailed analysis below.'}"
    
    # Add confidence indicator
    confidence_emoji = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}.get(confidence, "⚪")
    answer += f" {confidence_emoji} Confidence: {confidence}"
    
    return answer

# Ensure the upload directory exists
UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(page_title="Insurance Email Assistant", layout="wide")

st.markdown(
    """
    <style>
        body, .stApp {
            background-color: black;
            color: white;
        }
        .stTextArea, .stButton, .stJson {
            background-color: #111111;
        }
        .stTextArea textarea {
            background-color: #1e1e1e;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("LLM Insurance Document Processing System")
st.markdown("Choose how you'd like to analyze your insurance documents:")

# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = 'home'



# HOME PAGE - Main selection
if st.session_state.page == 'home':
    st.markdown("---")
    st.markdown("## 🎯 Choose Your Analysis Method")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin: 1rem 0;
            border: 2px solid #555;
        ">
            <h2 style="color: white; margin-bottom: 1rem;">📧 Email Analysis</h2>
            <p style="color: white; margin-bottom: 1.5rem;">Connect to your Gmail account and analyze insurance emails with attachments</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📧 Analyze Email Attachments", type="primary", use_container_width=True):
            st.session_state.page = 'email'
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin: 1rem 0;
            border: 2px solid #555;
        ">
            <h2 style="color: white; margin-bottom: 1rem;">📂 Document Upload</h2>
            <p style="color: white; margin-bottom: 1.5rem;">Upload your insurance policy documents and ask questions</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📂 Upload Document", type="primary", use_container_width=True):
            st.session_state.page = 'upload'
            st.rerun()

# EMAIL ANALYSIS PAGE
elif st.session_state.page == 'email':
    # Back button
    if st.button("← Back to Home", type="secondary"):
        st.session_state.page = 'home'
        st.rerun()
    
    st.markdown("---")
    st.markdown("## 📧 Email Analysis")
    st.markdown("### 🔐 Gmail Account Setup")
    selected_email_id = st.text_input("Enter a unique name for the Gmail account you'd like to use (e.g., yourname_token):", value="default")
    token_path = f"{selected_email_id}_token.pickle"
    
    # Step 1: Load filtered emails
    service = authenticate_gmail(token_path=token_path)
    emails = get_matching_emails(service)
    email_options = [f"{email['subject']} ({email['sender']})" for email in emails]
    selected_idx = st.selectbox("Select an email to analyze", range(len(email_options)), format_func=lambda i: email_options[i] if email_options else "No emails found")

    if emails:
        selected_email = emails[selected_idx]
        email_subject = selected_email.get("subject", "No subject")
        email_body = selected_email.get("body") or selected_email.get("snippet") or "No content found."

        # Clear previous session state to ensure fresh processing for each email selection
        if 'current_email_id' not in st.session_state or st.session_state.current_email_id != selected_email.get("id"):
            st.session_state.current_email_id = selected_email.get("id")
            st.session_state.processed_attachments = False

        attachment_texts = []
        attachment_chunks = []
        
        # Process attachments for the selected email
        if "attachment_paths" in selected_email and selected_email["attachment_paths"]:
            st.info(f"Processing {len(selected_email['attachment_paths'])} attachment(s)...")
            
            for path in selected_email["attachment_paths"]:
                try:
                    # Verify the file exists
                    if not os.path.exists(path):
                        st.warning(f"Attachment file not found: {path}")
                        continue
                        
                    if path.lower().endswith('.pdf'):
                        chunks = load_pdf(path)
                        attachment_text = "\n\n".join(chunk["content"] for chunk in chunks if "content" in chunk)
                        attachment_texts.append(f"PDF Content from {os.path.basename(path)}:\n{attachment_text}")
                        
                        # Add metadata to chunks for better tracking
                        for chunk in chunks:
                            chunk["metadata"]["email_id"] = selected_email.get("id")
                            chunk["metadata"]["email_subject"] = email_subject
                        attachment_chunks.extend(chunks)
                        
                    elif path.lower().endswith('.docx'):
                        chunks = load_docx(path)
                        attachment_text = "\n\n".join(chunk["content"] for chunk in chunks if "content" in chunk)
                        attachment_texts.append(f"DOCX Content from {os.path.basename(path)}:\n{attachment_text}")
                        
                        # Add metadata to chunks for better tracking
                        for chunk in chunks:
                            chunk["metadata"]["email_id"] = selected_email.get("id")
                            chunk["metadata"]["email_subject"] = email_subject
                        attachment_chunks.extend(chunks)
                        
                except Exception as e:
                    st.warning(f"Failed to read attachment {os.path.basename(path)}: {e}")
        
        # Add attachment chunks to vector store if they exist
        if attachment_chunks and not st.session_state.processed_attachments:
            try:
                # Clear existing index to avoid contamination from previous emails
                # (You might want to implement a more sophisticated approach for production)
                add_to_index(attachment_chunks)
                save_index()
                st.session_state.processed_attachments = True
                st.success(f"✅ Processed {len(attachment_chunks)} chunks from {len(selected_email['attachment_paths'])} attachment(s) into knowledge base.")
            except Exception as e:
                st.error(f"❌ Failed to add attachments to vector store: {e}")
                st.info("💡 Queries will use direct attachment content instead of vector store.")
        
        attachment_text = "\n\n".join(attachment_texts)

        with st.expander("📄 Preview Email Content"):
            st.markdown("**Email Subject:**")
            st.write(email_subject)

            st.markdown("**Email Body:**")
            st.write(email_body[:2000] + ("..." if len(email_body) > 2000 else ""))
            
            if attachment_text:
                st.markdown("**Attachment Content:**")
                st.write(attachment_text[:2000] + ("..." if len(attachment_text) > 2000 else ""))
                
            # Show which attachments were processed
            if "attachment_paths" in selected_email and selected_email["attachment_paths"]:
                st.markdown("**Processed Attachments:**")
                for i, path in enumerate(selected_email["attachment_paths"]):
                    st.write(f"• {os.path.basename(path)}")
                    
            if attachment_chunks:
                st.info(f"✅ {len(attachment_chunks)} document chunks ready for querying")
            else:
                st.warning("⚠️ No attachments to process - queries will use email content only")

        # User query input
        st.markdown("---")
        st.markdown("### 💬 Ask a Question About Your Email")
        
        # Use a form to prevent auto-submission on Enter
        with st.form("email_query_form"):
            user_query = st.text_input("Enter your question:", placeholder="e.g. Is my knee surgery covered?")
            submitted = st.form_submit_button("Get Answer", type="primary")

        if submitted and user_query.strip():
            final_query = user_query.strip()
            with st.spinner("Processing..."):
                # If we have attachments, use vector store search for more accurate results
                if attachment_chunks:
                    try:
                        load_index()
                        # Search for relevant chunks based on the query
                        relevant_chunks = search(final_query, top_k=5)
                        if relevant_chunks:
                            # Use vector store results
                            result = answer_query(final_query)
                            st.info("Answer based on processed attachments from vector store")
                        else:
                            # Fallback to direct context if no relevant chunks found
                            combined_context = f"Email Subject: {email_subject}\n\nEmail Body: {email_body}\n\nAttachment Content: {attachment_text}"
                            result = answer_query(final_query, context=combined_context)
                            st.info("Answer based on direct email and attachment content")
                    except Exception as e:
                        # Fallback to direct context if vector store fails
                        combined_context = f"Email Subject: {email_subject}\n\nEmail Body: {email_body}\n\nAttachment Content: {attachment_text}"
                        result = answer_query(final_query, context=combined_context)
                        st.warning(f"Vector store unavailable, using direct context: {e}")
                else:
                    # No attachments, use email content only
                    combined_context = f"Email Subject: {email_subject}\n\nEmail Body: {email_body}"
                    result = answer_query(final_query, context=combined_context)
                    st.info("Answer based on email content only (no attachments)")

            # Display the definitive answer
            st.markdown("## 🎯 **Answer**")
            
            definitive_answer = format_definitive_answer(result, final_query)
            st.markdown(definitive_answer)
            
            # Add spacing
            st.markdown("---")
            
            # Show JSON output in an expander
            with st.expander("🔍 **Click to see JSON structured output**"):
                st.json(result)
    else:
        st.warning("No relevant insurance-related emails found.")

# DOCUMENT UPLOAD PAGE
elif st.session_state.page == 'upload':
    # Back button
    if st.button("← Back to Home", type="secondary"):
        st.session_state.page = 'home'
        st.rerun()
    
    st.markdown("---")
    st.markdown("## 📂 Document Upload")
    st.markdown("### 📂 Upload Your Insurance Policy Document")

    uploaded_file = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"])

    if uploaded_file:
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded {uploaded_file.name} successfully!")

        # Just extract text for preview - don't process into vector store yet
        try:
            file_text = extract_text_from_file(uploaded_file, file_path)
            
            with st.expander("📄 Preview Uploaded Document"):
                st.write(file_text[:2000] + ("..." if len(file_text) > 2000 else ""))
        except Exception as e:
            st.error(f"Failed to read document: {e}")
            file_text = "Error reading document"

        st.markdown("---")
        st.markdown("### 💬 Ask a Question About Your Document")
        
        # Use a form to prevent auto-submission on Enter
        with st.form("doc_query_form"):
            user_query_doc = st.text_input("Enter your question:", placeholder="e.g. Does this cover ICU charges?")
            doc_submitted = st.form_submit_button("Get Answer from Document", type="primary")

        if doc_submitted and user_query_doc.strip():
            final_query_doc = user_query_doc.strip()
            with st.spinner("Processing document and generating answer..."):
                # Process uploaded document through vector store for better accuracy
                try:
                    if uploaded_file.name.lower().endswith('.pdf'):
                        doc_chunks = load_pdf(file_path)
                    elif uploaded_file.name.lower().endswith('.docx'):
                        doc_chunks = load_docx(file_path)
                    else:
                        doc_chunks = []
                    
                    if doc_chunks:
                        add_to_index(doc_chunks)
                        save_index()
                        load_index()
                        
                        # Search for relevant chunks
                        relevant_chunks = search(final_query_doc, top_k=5)
                        if relevant_chunks:
                            result = answer_query(final_query_doc)
                            st.info("Answer based on processed document from vector store")
                        else:
                            result = answer_query(final_query_doc, context=file_text)
                            st.info("Answer based on direct document content")
                    else:
                        result = answer_query(final_query_doc, context=file_text)
                        st.info("Answer based on direct document content")
                except Exception as e:
                    result = answer_query(final_query_doc, context=file_text)
                    st.warning(f"Vector store processing failed, using direct content: {e}")
            
            # Display the definitive answer
            st.markdown("## 🎯 **Answer**")
            
            definitive_answer = format_definitive_answer(result, final_query_doc)
            st.markdown(definitive_answer)
            
            # Add spacing
            st.markdown("---")
            
            # Show JSON output in an expander
            with st.expander("🔍 **Click to see JSON structured output**"):
                st.json(result)