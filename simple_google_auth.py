# simple_google_auth.py
"""
Simplified Google Authentication for ADK deployment.
No dependencies on config or logger modules.
"""

import os
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def get_google_service(api_name: str, api_version: str, scopes: list = None):
    """
    Get a Google API service instance.
    Simplified version for ADK deployment.
    """
    try:
        # Default scopes if not provided
        if scopes is None:
            if api_name == 'gmail':
                scopes = [
                    "https://www.googleapis.com/auth/gmail.readonly",
                    "https://www.googleapis.com/auth/gmail.modify",
                    "https://www.googleapis.com/auth/gmail.send"
                ]
            elif api_name == 'calendar':
                scopes = ["https://www.googleapis.com/auth/calendar"]
            elif api_name == 'drive':
                scopes = [
                    "https://www.googleapis.com/auth/drive.readonly",
                    "https://www.googleapis.com/auth/drive.file"
                ]
            else:
                scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        
        # Try service account first if configured
        service_account_path = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        if service_account_path and os.path.exists(service_account_path):
            creds = service_account.Credentials.from_service_account_file(
                service_account_path, 
                scopes=scopes
            )
        else:
            # Use OAuth2 flow
            creds = None
            token_path = 'token.json'
            credentials_path = 'credentials.json'
            
            # Try to load existing token
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, scopes)
            
            # Refresh or create new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if os.path.exists(credentials_path):
                        flow = InstalledAppFlow.from_client_secrets_file(
                            credentials_path, 
                            scopes
                        )
                        creds = flow.run_local_server(port=0)
                    else:
                        raise Exception(f"Credentials file not found: {credentials_path}")
                
                # Save credentials for future use
                with open(token_path, 'w') as token_file:
                    token_file.write(creds.to_json())
        
        # Build and return service
        service = build(api_name, api_version, credentials=creds)
        return service
        
    except Exception as e:
        raise Exception(f"Failed to create {api_name} service: {str(e)}")