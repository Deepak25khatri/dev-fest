"""
Centralized configuration management for Schedule-Agent.
Handles environment variables, API keys, and application settings.
"""

import os
from typing import Optional, List
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings with validation and defaults."""
    
    # Google API Configuration
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    use_vertex_ai: bool = Field(default=False, env="GOOGLE_GENAI_USE_VERTEXAI")
    google_service_account_path: Optional[str] = Field(default=None, env="GOOGLE_SERVICE_ACCOUNT_JSON")
    google_credentials_path: str = Field(default="credentials.json", env="GOOGLE_CREDENTIALS_PATH")
    google_token_path: str = Field(default="token.json", env="GOOGLE_TOKEN_PATH")
    
    # Application Configuration
    app_name: str = Field(default="schedule_agent_pa", env="APP_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Server Configuration
    port: int = Field(default=8080, env="PORT")
    host: str = Field(default="0.0.0.0", env="HOST")
    
    # Gmail Configuration
    gmail_max_results: int = Field(default=10, env="GMAIL_MAX_RESULTS")
    gmail_scopes: List[str] = Field(default=[
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.send"
    ])
    
    # Calendar Configuration
    calendar_scopes: List[str] = Field(default=[
        "https://www.googleapis.com/auth/calendar"
    ])
    
    # Drive Configuration
    drive_scopes: List[str] = Field(default=[
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/drive.file"
    ])
    
    # News/Search Configuration
    news_max_results: int = Field(default=7, env="NEWS_MAX_RESULTS")
    search_engine_id: Optional[str] = Field(default=None, env="GOOGLE_SEARCH_ENGINE_ID")
    
    # Security Configuration
    allowed_origins: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    max_request_size: int = Field(default=10485760, env="MAX_REQUEST_SIZE")  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

def get_google_scopes(service: str) -> List[str]:
    """Get appropriate scopes for a Google service."""
    scope_mapping = {
        "gmail": settings.gmail_scopes,
        "calendar": settings.calendar_scopes,
        "drive": settings.drive_scopes,
    }
    return scope_mapping.get(service, [])

def validate_config() -> bool:
    """Validate that required configuration is present."""
    if not settings.use_vertex_ai and not settings.google_api_key:
        print("❌ Error: GOOGLE_API_KEY is required when not using Vertex AI")
        return False
    
    if not os.path.exists(settings.google_credentials_path):
        print(f"❌ Error: Google credentials file not found at {settings.google_credentials_path}")
        return False
    
    print("✅ Configuration validated successfully")
    return True
