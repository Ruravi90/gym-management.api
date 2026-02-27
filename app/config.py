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

    # Mercado Pago configuration
    MP_ACCESS_TOKEN: str = os.getenv("MP_ACCESS_TOKEN", "TEST-1385641134871042-022619-4a77101c4d8f488c49f060464ed619dc-232825803")
    MP_PUBLIC_KEY: str = os.getenv("MP_PUBLIC_KEY", "TEST-be3a1a52-fc4e-4bf8-b5a5-4b69f83810b0")
    MP_WEBHOOK_URL: str = os.getenv("MP_WEBHOOK_URL", "https://gym-managementapi-production.up.railway.app/payments/webhook")
    MP_SUCCESS_URL: str = os.getenv("MP_SUCCESS_URL", "https://guerreros-panther.vercel.app/payment/success")
    MP_FAILURE_URL: str = os.getenv("MP_FAILURE_URL", "https://guerreros-panther.vercel.app/payment/failure")
    MP_PENDING_URL: str = os.getenv("MP_PENDING_URL", "https://guerreros-panther.vercel.app/payment/pending")

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