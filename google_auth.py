"""
Enhanced Google Authentication module with proper error handling, token refresh, and logging.
Supports both OAuth2 and Service Account authentication methods.
"""

import os
import json
from typing import Optional, List, Dict, Any
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import settings, get_google_scopes
from logger import logger, log_error, log_api_call

class GoogleAuthError(Exception):
    """Custom exception for Google authentication errors."""
    pass

class GoogleServiceManager:
    """Manages Google API service instances with proper authentication and error handling."""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._credentials: Optional[Credentials] = None
    
    def _get_credentials(self, scopes: List[str]) -> Credentials:
        """Get valid credentials for the given scopes."""
        try:
            # Try service account first if configured
            if settings.google_service_account_path and os.path.exists(settings.google_service_account_path):
                logger.info("Using service account authentication")
                creds = service_account.Credentials.from_service_account_file(
                    settings.google_service_account_path, 
                    scopes=scopes
                )
                return creds
            
            # Fall back to OAuth2 flow
            logger.info("Using OAuth2 authentication")
            creds = None
            
            # Try to load existing token
            if os.path.exists(settings.google_token_path):
                try:
                    creds = Credentials.from_authorized_user_file(settings.google_token_path, scopes)
                    logger.debug("Loaded existing credentials from token file")
                except Exception as e:
                    logger.warning(f"Failed to load existing credentials: {e}")
            
            # Refresh or create new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Refreshing expired credentials")
                    creds.refresh(Request())
                else:
                    logger.info("Creating new credentials via OAuth flow")
                    if not os.path.exists(settings.google_credentials_path):
                        raise GoogleAuthError(f"Credentials file not found: {settings.google_credentials_path}")
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        settings.google_credentials_path, 
                        scopes
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for future use
                with open(settings.google_token_path, 'w') as token_file:
                    token_file.write(creds.to_json())
                logger.info("Credentials saved for future use")
            
            return creds
            
        except Exception as e:
            log_error(e, "Google authentication")
            raise GoogleAuthError(f"Failed to authenticate with Google: {str(e)}")
    
    def get_service(self, api_name: str, api_version: str, scopes: Optional[List[str]] = None) -> Any:
        """Get a Google API service instance with proper authentication."""
        try:
            # Use service-specific scopes if not provided
            if scopes is None:
                scopes = get_google_scopes(api_name)
            
            # Create service key for caching
            service_key = f"{api_name}_{api_version}_{hash(tuple(scopes))}"
            
            # Return cached service if available
            if service_key in self._services:
                logger.debug(f"Returning cached service for {api_name}")
                return self._services[service_key]
            
            # Get credentials
            creds = self._get_credentials(scopes)
            
            # Build service
            log_api_call("Google", f"build_{api_name}", version=api_version)
            service = build(api_name, api_version, credentials=creds)
            
            # Cache service
            self._services[service_key] = service
            logger.info(f"Created new service for {api_name} v{api_version}")
            
            return service
            
        except Exception as e:
            log_error(e, f"Google service creation for {api_name}")
            raise GoogleAuthError(f"Failed to create {api_name} service: {str(e)}")
    
    def clear_cache(self):
        """Clear cached services (useful for testing or credential refresh)."""
        self._services.clear()
        logger.info("Cleared service cache")

# Global service manager instance
service_manager = GoogleServiceManager()

def get_google_service(api_name: str, api_version: str, scopes: Optional[List[str]] = None) -> Any:
    """
    Get a Google API service instance.
    
    Args:
        api_name: Name of the Google API (e.g., 'gmail', 'calendar', 'drive')
        api_version: API version (e.g., 'v1', 'v3')
        scopes: List of OAuth scopes (optional, will use defaults if not provided)
    
    Returns:
        Google API service instance
        
    Raises:
        GoogleAuthError: If authentication or service creation fails
    """
    return service_manager.get_service(api_name, api_version, scopes)

def validate_credentials() -> bool:
    """Validate that credentials are properly configured and working."""
    try:
        # Test with a simple API call
        service = get_google_service('gmail', 'v1')
        # Try to get user profile to validate credentials
        profile = service.users().getProfile(userId='me').execute()
        logger.info(f"Credentials validated for user: {profile.get('emailAddress', 'Unknown')}")
        return True
    except Exception as e:
        log_error(e, "Credential validation")
        return False

def refresh_credentials() -> bool:
    """Force refresh of credentials."""
    try:
        service_manager.clear_cache()
        return validate_credentials()
    except Exception as e:
        log_error(e, "Credential refresh")
        return False
