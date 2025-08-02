"""
Configuration module for loading environment variables
Manages Aiven URI, API keys, and other settings
"""
import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database
    aiven_postgres_uri: str = os.getenv("AIVEN_POSTGRES_URI", "")
    
    # API Configuration
    api_key: Optional[str] = os.getenv("API_KEY")
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key")
    
    # External Services
    maps_api_key: Optional[str] = os.getenv("MAPS_API_KEY")
    weather_api_key: Optional[str] = os.getenv("WEATHER_API_KEY")
    
    # Application Settings
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
