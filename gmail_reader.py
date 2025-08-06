import os
import base64
import pickle
import re
from typing import List, Dict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

# Gmail read-only scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

ATTACHMENTS_DIR = "email_attachments"
os.makedirs(ATTACHMENTS_DIR, exist_ok=True)

KEYWORDS = [  # Add as needed or pull from external
    "insurance policy", "policy number", "coverage", "claim", "claim approved",
    "surgery", "hospitalization", "insured", "Pune", "premium", "attached", "eligibility"
]

EXCLUDE_KEYWORDS = [
    "car insurance", "vehicle insurance", "motor insurance",
    "four wheeler", "two wheeler", "bike insurance",
    "travel insurance", "trip", "journey", "railway", "train", "pnr", "flight", "airline",
    "maruti", "ritz", "tvs", "honda", "hyundai", "suzuki", "yamaha", "bajaj", "toyota", "nexa"
]

def authenticate_gmail(token_path="token.pickle", credentials_path="credentials.json"):
    creds = None

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)


def get_matching_emails(service, max_results=10) -> List[Dict]:
    # Relaxed query: fetch more emails and filter in Python
    results = service.users().messages().list(userId='me', q="", maxResults=max_results * 5).execute()
    messages = results.get('messages', [])

    matched_emails = []

    def extract_text_parts(payload, msg_id):
        text_parts = []
        attachment_paths_local = []
        
        if 'parts' in payload:
            for part in payload['parts']:
                # Handle nested parts (e.g., multipart/alternative)
                if 'parts' in part:
                    nested_texts, nested_attachments = extract_text_parts(part, msg_id)
                    text_parts.extend(nested_texts)
                    attachment_paths_local.extend(nested_attachments)
                else:
                    # This is a leaf part, process it for content
                    if part.get('mimeType') == 'text/plain' and 'data' in part.get('body', {}):
                        decoded_data = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                        text_parts.append(decoded_data)
                    
                    elif part.get('mimeType') == 'text/html' and 'data' in part.get('body', {}):
                        html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                        soup = BeautifulSoup(html, 'html.parser')
                        text_parts.append(soup.get_text())

                # Handle attachments at the same level as parts
                if part.get('filename') and part['filename'].lower().endswith(('.pdf', '.docx')):
                    if 'attachmentId' in part.get('body', {}):
                        attachment_path = save_attachment(service, msg_id, part, part['filename'])
                        if attachment_path:
                            attachment_paths_local.append(attachment_path)
            
            if not text_parts and 'body' in payload and 'data' in payload['body']:
                fallback_text = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
                text_parts.append(fallback_text)
        
        # Handle non-multipart emails
        elif 'body' in payload and 'data' in payload['body']:
            if payload.get('mimeType') == 'text/plain':
                text_parts.append(base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore'))
            elif payload.get('mimeType') == 'text/html':
                html = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
                soup = BeautifulSoup(html, 'html.parser')
                text_parts.append(soup.get_text())

        return text_parts, attachment_paths_local

    for msg in messages:
        full_msg = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = full_msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown sender')

        # Recursively extract all text parts and attachments
        body_parts, attachment_paths = extract_text_parts(full_msg['payload'], msg['id'])
        body = "\n".join([b for b in body_parts if b.strip()])
        if not body:
            body = "No body"
        snippet = re.sub(r'\s+', ' ', body.strip())[:300]

        subject_lower = subject.lower()
        snippet_lower = snippet.lower()
        body_lower = body.lower()

        # Python-side keyword filter: match in subject, snippet, or body OR has attachments
        keyword_found = any(k.lower() in subject_lower or k.lower() in snippet_lower or k.lower() in body_lower for k in KEYWORDS)
        has_insurance_attachments = bool(attachment_paths)  # Include emails with PDF/DOCX attachments
        
        if not keyword_found and not has_insurance_attachments:
            continue  # Skip only if no keyword and no relevant attachments

        # Exclusion filter: skip if exclusion keyword in subject, snippet, or body
        exclusion_found = any(exclude in subject_lower or exclude in snippet_lower or exclude in body_lower for exclude in EXCLUDE_KEYWORDS)
        if exclusion_found and not has_insurance_attachments:
            continue  # Skip emails with excluded keywords, but keep if they have attachments

        if not any(email.get('id') == msg['id'] for email in matched_emails):
            entry = {
                "id": msg["id"],
                "subject": subject,
                "sender": sender,
                "snippet": snippet,
                "body": body
            }
            if attachment_paths:
                entry["attachment_paths"] = attachment_paths
            matched_emails.append(entry)
    return matched_emails

def save_attachment(service, msg_id, part, filename):
    attachment_id = part['body']['attachmentId']
    attachment = service.users().messages().attachments().get(userId='me', messageId=msg_id, id=attachment_id).execute()
    data = base64.urlsafe_b64decode(attachment['data'])
    filepath = os.path.join(ATTACHMENTS_DIR, filename)
    with open(filepath, 'wb') as f:
        f.write(data)
    return filepath

def get_email_body(service, msg_id: str) -> str:
    full_msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()

    if 'parts' in full_msg['payload']:
        for part in full_msg['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
            elif part['mimeType'] == 'text/html':
                html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                return BeautifulSoup(html, 'html.parser').get_text()
    else:
        return base64.urlsafe_b64decode(full_msg['payload']['body']['data']).decode('utf-8', errors='ignore')

    return ""

def get_filtered_emails():
    service = authenticate_gmail()
    return get_matching_emails(service)

if __name__ == "__main__":
    service = authenticate_gmail()
    emails = get_matching_emails(service)
    for e in emails:
        print(f"\n=== {e['subject']} ({e['sender']}) ===\n{e['snippet']}\n")