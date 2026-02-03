from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Application
    APP_NAME: str = "Healthcare AI Microservice"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://healthcare_user:healthcare_pass@localhost:5432/healthcare_db"
    VECTOR_DB_URL: Optional[str] = None  # Same as DATABASE_URL if not specified
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # AWS Credentials
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    
    # AWS Bedrock
    BEDROCK_REGION: str = "us-east-1"
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    BEDROCK_MAX_TOKENS: int = 2048
    BEDROCK_EMBEDDING_MODEL: str = "amazon.titan-embed-text-v1"
    
    # AWS Textract
    TEXTRACT_REGION: str = "us-east-1"
    
    # Security
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Storage (Mock - Local Filesystem)
    DOCUMENT_STORAGE_PATH: str = "_documents"
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_DOCUMENT_TYPES: list = [".pdf", ".jpg", ".jpeg", ".png"]
    
    # RAG Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    EMBEDDING_DIMENSION: int = 1536
    TOP_K_PATIENT_CHAT: int = 5
    TOP_K_DOCTOR_CHAT: int = 10
    
    # Feature Flags
    ENABLE_VISION_ANALYSIS: bool = True
    ENABLE_AUTO_RAG_REFRESH: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields from .env
    )


# Global settings instance
settings = Settings()
