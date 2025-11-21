"""
Configuration management for Medical Data Extraction API
"""
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Base configuration"""
    
    # Application
    APP_NAME = os.getenv("APP_NAME", "Medical Data Extraction API")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://meduser:medpassword@localhost:5432/medical_data_db"
    )
    DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "5"))
    DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
    
    # OCR
    OCR_ENGINE = os.getenv("OCR_ENGINE", "easyocr")
    OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "en").split(",")
    TESSERACT_PATH = os.getenv("TESSERACT_PATH", "/usr/bin/tesseract")
    OCR_CONFIDENCE_THRESHOLD = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.6"))
    
    # File Upload
    UPLOAD_FOLDER = Path(os.getenv("UPLOAD_FOLDER", "data/uploads"))
    PROCESSED_FOLDER = Path(os.getenv("PROCESSED_FOLDER", "data/processed"))
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    ALLOWED_EXTENSIONS = set(
        os.getenv("ALLOWED_EXTENSIONS", "pdf,png,jpg,jpeg,tiff").split(",")
    )
    
    # HIPAA Compliance
    ENABLE_AUDIT_LOG = os.getenv("ENABLE_AUDIT_LOG", "True").lower() == "true"
    ENCRYPTION_ENABLED = os.getenv("ENCRYPTION_ENABLED", "True").lower() == "true"
    DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", "2555"))  # 7 years
    PHI_REDACTION_ENABLED = os.getenv("PHI_REDACTION_ENABLED", "True").lower() == "true"
    
    # API
    API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8000"
    ).split(",")
    RATE_LIMIT = os.getenv("RATE_LIMIT", "100/hour")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = Path(os.getenv("LOG_FILE", "logs/app.log"))
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Email
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    
    @classmethod
    def init_app(cls):
        """Initialize application directories"""
        cls.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = "sqlite:///test.db"


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Get configuration based on environment"""
    env = os.getenv("APP_ENV", "development")
    return config.get(env, config["default"])
