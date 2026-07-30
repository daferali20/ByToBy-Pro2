import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "ByToBy Pro2 AI"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/bytoby")
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_DB: int = 0
    REDIS_EXPIRE: int = 3600
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list = ["http://localhost:3000"]
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # External APIs
    ALPHA_VANTAGE_KEY: str = os.getenv("ALPHA_VANTAGE_KEY", "")
    FINNHUB_KEY: str = os.getenv("FINNHUB_KEY", "")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    
    # AI Models
    ML_MODELS_PATH: str = "models/"
    TENSORFLOW_GPU: bool = False
    BATCH_SIZE: int = 32
    EPOCHS: int = 100
    
    # Scheduler
    SCHEDULER_TIMEZONE: str = "America/New_York"
    UPDATE_INTERVAL_MINUTES: int = 5
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
