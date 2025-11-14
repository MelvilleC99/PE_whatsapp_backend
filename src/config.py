"""
Configuration management using pydantic-settings
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Meta WhatsApp Business API
    whatsapp_access_token: str = Field(..., description="Meta access token")
    whatsapp_phone_number_id: str = Field(..., description="WhatsApp phone number ID")
    whatsapp_business_account_id: str = Field(..., description="Business account ID")
    meta_app_id: Optional[str] = None
    meta_app_secret: Optional[str] = None
    webhook_verify_token: str = Field(..., description="Webhook verification token for Meta")
    
    # Meta API Configuration
    meta_api_version: str = "v18.0"
    meta_api_base_url: str = "https://graph.facebook.com"
    
    # Firebase
    firebase_project_id: str
    firebase_private_key: str
    firebase_client_email: str
    
    # Database
    database_host: str
    database_port: int = 5432
    database_name: str
    database_user: str
    database_password: str
    
    # Application
    environment: str = "development"
    log_level: str = "INFO"
    timezone: str = "Africa/Johannesburg"
    
    # Scheduling
    insights_schedule: str = "0 9 * * 1"  # Every Monday at 9 AM
    
    @property
    def meta_graph_api_url(self) -> str:
        """Construct Meta Graph API base URL"""
        return f"{self.meta_api_base_url}/{self.meta_api_version}"
    
    @property
    def firebase_credentials_dict(self) -> dict:
        """Generate Firebase credentials dictionary"""
        return {
            "type": "service_account",
            "project_id": self.firebase_project_id,
            "private_key": self.firebase_private_key.replace('\\n', '\n'),
            "client_email": self.firebase_client_email,
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        }
    
    @property
    def database_url(self) -> str:
        """Construct database connection URL"""
        return f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"


# Global settings instance
settings = Settings()


if __name__ == "__main__":
    # Test configuration loading
    print("✅ Configuration loaded successfully!")
    print(f"Environment: {settings.environment}")
    print(f"Meta API: {settings.meta_graph_api_url}")
    print(f"Firebase Project: {settings.firebase_project_id}")
    print(f"Database: {settings.database_host}:{settings.database_port}")
