from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database Configuration
    MONGODB_URL: str = "mongodb://localhost:27017/dinov3_db"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Cloudflare R2 Configuration
    CLOUDFLARE_R2_ENDPOINT: str = "https://026089839555deec85ae1cfc77648038.r2.cloudflarestorage.com"
    CLOUDFLARE_R2_ACCESS_KEY_ID: str = "bd49d02c53d50486bf43b8c1c7d6451d"
    CLOUDFLARE_R2_SECRET_ACCESS_KEY: str = "1b06a8ab4e537af7a35891c73ba50b5edf3e665f6044897777eecdcf8e5fff9c"
    CLOUDFLARE_R2_BUCKET_NAME: str = "rumble-fanz"
    CLOUDFLARE_R2_PUBLIC_URL: str = "https://media.rumbletv.com"
    
    # DINOv3 Model Configuration
    DINOV3_MODEL_NAME: str = "models/dinov3-vitb16-pretrain-lvd1689m"
    DINOV3_DEVICE: str = "cuda"
    DINOV3_BATCH_SIZE: int = 32
    DINOV3_CACHE_SIZE: int = 1000
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 3012
    API_WORKERS: int = 1
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Processing Limits
    MAX_FILE_SIZE_MB: int = 50
    MAX_BATCH_SIZE: int = 100
    REQUEST_TIMEOUT_SECONDS: int = 300
    
    # Quality Thresholds
    DEFAULT_QUALITY_THRESHOLD: float = 0.7
    DEFAULT_SIMILARITY_THRESHOLD: float = 75.0
    
    # PathRAG Configuration
    PATHRAG_API_URL: str = "http://localhost:5000"
    PATHRAG_ENABLE: bool = True
    PATHRAG_DEFAULT_TOP_K: int = 40
    PATHRAG_MAX_TOKEN_FOR_TEXT_UNIT: int = 4000
    PATHRAG_MAX_TOKEN_FOR_GLOBAL_CONTEXT: int = 3000
    PATHRAG_MAX_TOKEN_FOR_LOCAL_CONTEXT: int = 5000
    
    # External Services
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in .env file

# Global settings instance
settings = Settings()
