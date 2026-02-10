import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database configuration - Railway often provides DATABASE_URL
    #DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://app:Ruravi90@127.0.0.1:3306/GymControl")
    DATABASE_URL: str = os.getenv("DATABASE_URL_DEV", "mysql+pymysql://root:fknwSVioguFJzVGwyMJzkKDBZApslDlt@turntable.proxy.rlwy.net:49303/railway")
    # Secret key for JWT tokens - should be set in Railway environment
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-123-change-in-production")

    # Algorithm for JWT
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    # Token expiration (in minutes) - 24 hours = 1440 minutes
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # Port for the application (Railway sets PORT environment variable)
    PORT: int = int(os.getenv("PORT", "8000"))

    # Environment (development, staging, production)
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Allow CORS origin (for Railway deployment)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "*")

settings = Settings()
