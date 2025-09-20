# custom_drive_tool.py
"""
Custom Drive Tool for Schedule-Agent.
Provides comprehensive Google Drive operations as Google ADK Function Tools.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from googleapiclient.errors import HttpError
from google.adk.tools import FunctionTool
from simple_google_auth import get_google_service

def _get_drive_service():
    """Get Drive service instance."""
    return get_google_service('drive', 'v3')

def search_drive_files(query: str, max_results: int = 20) -> str:
    """Search for files in Google Drive."""
    try:
        service = _get_drive_service()
        
        if not query or not query.strip():
            return "❌ Search query cannot be empty"
        
        # Search files
        results = service.files().list(
            q=query.strip(),
            pageSize=max_results,
            fields="files(id, name, mimeType, owners, modifiedTime, webViewLink, size)"
        ).execute()
        
        files = results.get('files', [])
        if not files:
            return f"No files found for query: '{query}'"
        
        # Format output
        output = f"📁 Found {len(files)} files for '{query}':\n\n"
        for i, file in enumerate(files, 1):
            owner = file.get('owners', [{}])[0].get('displayName', 'Unknown')
            modified = file.get('modifiedTime', 'Unknown')
            size = file.get('size', 'Unknown')
            link = file.get('webViewLink', 'No link')
            
            output += f"{i}. **{file.get('name', 'Unknown')}**\n"
            output += f"   Type: {file.get('mimeType', 'Unknown')}\n"
            output += f"   Owner: {owner}\n"
            output += f"   Modified: {modified}\n"
            output += f"   Size: {size} bytes\n"
            output += f"   Link: {link}\n\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error searching Drive files: {str(e)}"

def get_file_content(file_id: str) -> str:
    """Get the content of a Google Drive file."""
    try:
        service = _get_drive_service()
        
        # Get file metadata
        file_metadata = service.files().get(fileId=file_id).execute()
        file_name = file_metadata.get('name', 'Unknown')
        mime_type = file_metadata.get('mimeType', '')
        
        # Handle different file types
        if 'document' in mime_type:
            # Google Docs
            content = service.files().export_media(
                fileId=file_id, 
                mimeType='text/plain'
            ).execute()
            content_text = content.decode('utf-8')
        elif 'spreadsheet' in mime_type:
            # Google Sheets
            content_text = f"📊 Google Sheets file: {file_name}\n"
            content_text += "To view the full spreadsheet, please open the file directly in Google Sheets."
        elif 'presentation' in mime_type:
            # Google Slides
            content_text = f"��️ Google Slides file: {file_name}\n"
            content_text += "To view the full presentation, please open the file directly in Google Slides."
        else:
            # Other file types
            content_text = f"📄 File: {file_name}\n"
            content_text += f"Type: {mime_type}\n"
            content_text += "This file type cannot be previewed as text."
        
        return f"📄 **{file_name}**\n\n{content_text}"
        
    except Exception as e:
        return f"❌ Error retrieving file content: {str(e)}"

def list_recent_files(max_results: int = 10) -> str:
    """List recently modified files in Google Drive."""
    try:
        service = _get_drive_service()
        
        # Get recent files
        results = service.files().list(
            pageSize=max_results,
            orderBy='modifiedTime desc',
            fields="files(id, name, mimeType, owners, modifiedTime, webViewLink, size)"
        ).execute()
        
        files = results.get('files', [])
        if not files:
            return "No recent files found."
        
        # Format output
        output = f"📁 Recent {len(files)} files:\n\n"
        for i, file in enumerate(files, 1):
            owner = file.get('owners', [{}])[0].get('displayName', 'Unknown')
            modified = file.get('modifiedTime', 'Unknown')
            size = file.get('size', 'Unknown')
            
            output += f"{i}. **{file.get('name', 'Unknown')}**\n"
            output += f"   Type: {file.get('mimeType', 'Unknown')}\n"
            output += f"   Owner: {owner}\n"
            output += f"   Modified: {modified}\n"
            output += f"   Size: {size} bytes\n\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error listing recent files: {str(e)}"

def share_file(file_id: str, email: str, role: str = 'reader') -> str:
    """Share a Google Drive file with someone."""
    try:
        service = _get_drive_service()
        
        # Create permission
        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }
        
        # Share the file
        result = service.permissions().create(
            fileId=file_id,
            body=permission,
            sendNotificationEmail=True
        ).execute()
        
        return f"✅ File shared successfully!\nShared with: {email}\nRole: {role}\nPermission ID: {result.get('id', 'Unknown')}"
        
    except Exception as e:
        return f"❌ Error sharing file: {str(e)}"

def get_drive_info() -> str:
    """Get information about Google Drive storage."""
    try:
        service = _get_drive_service()
        
        # Get storage quota
        about = service.about().get(fields='storageQuota').execute()
        quota = about.get('storageQuota', {})
        
        total = int(quota.get('limit', 0))
        used = int(quota.get('usage', 0))
        available = total - used
        
        # Convert to GB
        total_gb = total / (1024**3)
        used_gb = used / (1024**3)
        available_gb = available / (1024**3)
        
        output = f"�� **Google Drive Storage Info**\n\n"
        output += f"Total Storage: {total_gb:.2f} GB\n"
        output += f"Used Storage: {used_gb:.2f} GB\n"
        output += f"Available Storage: {available_gb:.2f} GB\n"
        output += f"Usage: {(used/total*100):.1f}%"
        
        return output
        
    except Exception as e:
        return f"❌ Error retrieving Drive info: {str(e)}"

# Create Google ADK Function Tools
drive_tools = [
    FunctionTool.from_defaults(
        name="search_drive_files",
        description="Search for files in Google Drive by name, type, or content",
        func=search_drive_files
    ),
    FunctionTool.from_defaults(
        name="get_file_content",
        description="Get the content of a Google Drive file by file ID",
        func=get_file_content
    ),
    FunctionTool.from_defaults(
        name="list_recent_files",
        description="List recently modified files in Google Drive",
        func=list_recent_files
    ),
    FunctionTool.from_defaults(
        name="share_file",
        description="Share a Google Drive file with someone by email",
        func=share_file
    ),
    FunctionTool.from_defaults(
        name="get_drive_info",
        description="Get Google Drive storage information",
        func=get_drive_info
    )
]