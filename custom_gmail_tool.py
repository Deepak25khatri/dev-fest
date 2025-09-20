# custom_gmail_tool.py
"""
Custom Gmail Tool for Schedule-Agent.
Provides comprehensive Gmail operations as Google ADK Function Tools.
"""

import base64
from email.mime.text import MIMEText
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from googleapiclient.errors import HttpError
from google.adk.tools import FunctionTool
from simple_google_auth import get_google_service

def _get_gmail_service():
    """Get Gmail service instance."""
    return get_google_service('gmail', 'v1')

def _format_email_summary(message: Dict[str, Any]) -> Dict[str, Any]:
    """Format email data for consistent output."""
    headers = message.get('payload', {}).get('headers', [])
    header_dict = {h['name'].lower(): h['value'] for h in headers}
    
    return {
        'id': message['id'],
        'thread_id': message['threadId'],
        'subject': header_dict.get('subject', '(No Subject)'),
        'sender': header_dict.get('from', 'Unknown'),
        'recipient': header_dict.get('to', 'Unknown'),
        'date': header_dict.get('date', 'Unknown'),
        'snippet': message.get('snippet', ''),
        'labels': message.get('labelIds', []),
        'size': message.get('sizeEstimate', 0)
    }

def get_unread_emails(max_results: int = 10) -> str:
    """Get a summary of unread emails with key details."""
    try:
        service = _get_gmail_service()
        
        # Get unread messages
        results = service.users().messages().list(
            userId='me',
            labelIds=['UNREAD'],
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        if not messages:
            return "No unread emails found."
        
        # Get detailed information for each message
        summaries = []
        for msg in messages:
            try:
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                summaries.append(_format_email_summary(message))
            except HttpError as e:
                continue
        
        # Format output
        output = f"📧 Found {len(summaries)} unread emails:\n\n"
        for i, email in enumerate(summaries, 1):
            output += f"{i}. **{email['subject']}**\n"
            output += f"   From: {email['sender']}\n"
            output += f"   Date: {email['date']}\n"
            output += f"   Preview: {email['snippet'][:100]}...\n\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error retrieving unread emails: {str(e)}"

def search_emails(query: str, max_results: int = 20) -> str:
    """Search emails using Gmail search syntax."""
    try:
        service = _get_gmail_service()
        
        if not query or not query.strip():
            return "❌ Search query cannot be empty"
        
        # Search messages
        results = service.users().messages().list(
            userId='me',
            q=query.strip(),
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        if not messages:
            return f"No emails found for query: '{query}'"
        
        # Get detailed information for each message
        search_results = []
        for msg in messages:
            try:
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                search_results.append(_format_email_summary(message))
            except HttpError as e:
                continue
        
        # Format output
        output = f"🔍 Found {len(search_results)} emails for '{query}':\n\n"
        for i, email in enumerate(search_results, 1):
            output += f"{i}. **{email['subject']}**\n"
            output += f"   From: {email['sender']}\n"
            output += f"   Date: {email['date']}\n"
            output += f"   Preview: {email['snippet'][:100]}...\n\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error searching emails: {str(e)}"

def get_email_content(message_id: str) -> str:
    """Get full content of a specific email."""
    try:
        service = _get_gmail_service()
        
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        # Extract text content
        content = _extract_text_content(message.get('payload', {}))
        
        # Format output
        email_info = _format_email_summary(message)
        output = f"📧 **{email_info['subject']}**\n"
        output += f"From: {email_info['sender']}\n"
        output += f"Date: {email_info['date']}\n"
        output += f"To: {email_info['recipient']}\n\n"
        output += "**Content:**\n"
        output += content
        
        return output
        
    except Exception as e:
        return f"❌ Error retrieving email content: {str(e)}"

def _extract_text_content(payload: Dict[str, Any]) -> str:
    """Extract text content from email payload."""
    content = ""
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part.get('body', {}).get('data', '')
                if data:
                    content += base64.urlsafe_b64decode(data).decode('utf-8')
            elif part['mimeType'] == 'text/html':
                data = part.get('body', {}).get('data', '')
                if data:
                    content += base64.urlsafe_b64decode(data).decode('utf-8')
            elif 'parts' in part:
                content += _extract_text_content(part)
    else:
        if payload.get('mimeType') == 'text/plain':
            data = payload.get('body', {}).get('data', '')
            if data:
                content = base64.urlsafe_b64decode(data).decode('utf-8')
    
    return content

def draft_email(to: Union[str, List[str]], subject: str, body: str, 
               cc: Optional[Union[str, List[str]]] = None,
               bcc: Optional[Union[str, List[str]]] = None) -> str:
    """Create a draft email (not sent automatically)."""
    try:
        service = _get_gmail_service()
        
        # Create message
        message = MIMEText(body)
        message['to'] = ', '.join(to) if isinstance(to, list) else to
        message['subject'] = subject
        
        if cc:
            message['cc'] = ', '.join(cc) if isinstance(cc, list) else cc
        if bcc:
            message['bcc'] = ', '.join(bcc) if isinstance(bcc, list) else bcc
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Create draft
        draft = service.users().drafts().create(
            userId='me',
            body={'message': {'raw': raw_message}}
        ).execute()
        
        return f"✅ Draft email created successfully!\nDraft ID: {draft['id']}\nTo: {message['to']}\nSubject: {subject}"
        
    except Exception as e:
        return f"❌ Error creating draft email: {str(e)}"

def send_email(to: Union[str, List[str]], subject: str, body: str,
              cc: Optional[Union[str, List[str]]] = None,
              bcc: Optional[Union[str, List[str]]] = None) -> str:
    """Send an email immediately."""
    try:
        service = _get_gmail_service()
        
        # Create message
        message = MIMEText(body)
        message['to'] = ', '.join(to) if isinstance(to, list) else to
        message['subject'] = subject
        
        if cc:
            message['cc'] = ', '.join(cc) if isinstance(cc, list) else cc
        if bcc:
            message['bcc'] = ', '.join(bcc) if isinstance(bcc, list) else bcc
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send message
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return f"✅ Email sent successfully!\nMessage ID: {sent_message['id']}\nTo: {message['to']}\nSubject: {subject}"
        
    except Exception as e:
        return f"❌ Error sending email: {str(e)}"

def organize_email(message_id: str, action: str, label_id: Optional[str] = None) -> str:
    """Organize email: apply label, archive, delete, mark as read/unread."""
    try:
        service = _get_gmail_service()
        
        if action == 'delete':
            service.users().messages().delete(
                userId='me',
                id=message_id
            ).execute()
            return f"✅ Email {message_id} deleted successfully"
            
        elif action == 'archive':
            service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['INBOX']}
            ).execute()
            return f"✅ Email {message_id} archived successfully"
            
        elif action == 'add_label' and label_id:
            service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            return f"✅ Label '{label_id}' added to email {message_id}"
            
        elif action == 'remove_label' and label_id:
            service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': [label_id]}
            ).execute()
            return f"✅ Label '{label_id}' removed from email {message_id}"
            
        elif action == 'mark_read':
            service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return f"✅ Email {message_id} marked as read"
            
        elif action == 'mark_unread':
            service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': ['UNREAD']}
            ).execute()
            return f"✅ Email {message_id} marked as unread"
            
        else:
            return f"❌ Unknown action: {action}. Available actions: delete, archive, add_label, remove_label, mark_read, mark_unread"
        
    except Exception as e:
        return f"❌ Error organizing email: {str(e)}"

def get_gmail_labels() -> str:
    """Get all Gmail labels."""
    try:
        service = _get_gmail_service()
        
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        if not labels:
            return "No Gmail labels found."
        
        output = f"��️ Found {len(labels)} Gmail labels:\n\n"
        for label in labels:
            output += f"• {label.get('name', 'Unknown')}\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error retrieving labels: {str(e)}"

# Create Google ADK Function Tools
gmail_tools = [
    FunctionTool.from_defaults(
        name="get_unread_emails",
        description="Get a summary of unread emails with sender, subject, date, and preview",
        func=get_unread_emails
    ),
    FunctionTool.from_defaults(
        name="search_emails",
        description="Search emails using Gmail search syntax (from:, to:, subject:, has:attachment, etc.)",
        func=search_emails
    ),
    FunctionTool.from_defaults(
        name="get_email_content",
        description="Get the full content of a specific email by message ID",
        func=get_email_content
    ),
    FunctionTool.from_defaults(
        name="draft_email",
        description="Create a draft email (not sent automatically)",
        func=draft_email
    ),
    FunctionTool.from_defaults(
        name="send_email",
        description="Send an email immediately",
        func=send_email
    ),
    FunctionTool.from_defaults(
        name="organize_email",
        description="Organize email: delete, archive, add/remove labels, mark as read/unread",
        func=organize_email
    ),
    FunctionTool.from_defaults(
        name="get_gmail_labels",
        description="Get all available Gmail labels",
        func=get_gmail_labels
    )
]