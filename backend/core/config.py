import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://root:example123@localhost:27017/?authSource=admin")
    database_name: str = os.getenv("DATABASE_NAME", "mongo_test_db")
    secret_key: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production")
    
    # JWT settings
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Cleanup settings
    tmp_files_max_age_hours: int = int(os.getenv("TMP_FILES_MAX_AGE_HOURS", "24"))  # Delete after 24 hours
    cleanup_interval_minutes: int = int(os.getenv("CLEANUP_INTERVAL_MINUTES", "60"))  # Run cleanup every hour
    max_tmp_storage_mb: int = int(os.getenv("MAX_TMP_STORAGE_MB", "1000"))  # Alert if tmp storage > 1GB
    enable_cleanup_scheduler: bool = os.getenv("ENABLE_CLEANUP_SCHEDULER", "true").lower() == "true"  # Enable/disable auto cleanup
    
    class Config:
        env_file = ".env"


settings = Settings()
