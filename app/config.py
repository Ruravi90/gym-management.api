import os
import warnings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database configuration for Tortoise ORM
    #DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql://root:fknwSVioguFJzVGwyMJzkKDBZApslDlt@turntable.proxy.rlwy.net:49303/railway")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql://app:Ruravi90@localhost:3306/GymControl")
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

# Warn if using default secret key
if settings.SECRET_KEY == "your-secret-key-123-change-in-production":
    if settings.ENVIRONMENT == "production":
        raise RuntimeError("SECRET_KEY must be set in production! Set the SECRET_KEY environment variable.")
    else:
        warnings.warn("Using default SECRET_KEY. Set SECRET_KEY env var for production.", stacklevel=2)

# Configuration for Tortoise ORM with optimizations
TORTOISE_CONFIG = {
    "connections": {
        "default": settings.DATABASE_URL
    },
    "apps": {
        "models": {
            "models": ["app.models"],
            "default_connection": "default",
        },
        "aerich": {
            "models": ["aerich.models"],
            "default_connection": "default",
        }
    },
    "use_tz": False,
    "timezone": "UTC",
    # Performance optimizations
    "_comment": "Pool configuration for MySQL connections",
    "db_client_kwargs": {
        "charset": "utf8mb4",
        "sql_mode": "STRICT_TRANS_TABLES",
        "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
    }
}