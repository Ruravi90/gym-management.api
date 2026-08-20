import os
import warnings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database configuration for Tortoise ORM
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    # Secret key for JWT tokens - should be set in Railway environment
    SECRET_KEY: str = os.getenv("SECRET_KEY")

    # Algorithm for JWT
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    # Token expiration (in minutes) - 24 hours = 1440 minutes
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # Refresh token expiration (in days) - 30 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

    # Port for the application (Railway sets PORT environment variable)
    PORT: int = int(os.getenv("PORT", "8000"))

    # Environment (development, staging, production)
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")

    # Allow CORS origin (for Railway deployment)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "*")

    # Mercado Pago configuration
    MP_ACCESS_TOKEN: str = os.getenv("MP_ACCESS_TOKEN", "")
    MP_PUBLIC_KEY: str = os.getenv("MP_PUBLIC_KEY", "")
    MP_WEBHOOK_URL: str = os.getenv("MP_WEBHOOK_URL", "")
    MP_SUCCESS_URL: str = os.getenv("MP_SUCCESS_URL", "")
    MP_FAILURE_URL: str = os.getenv("MP_FAILURE_URL", "")
    MP_PENDING_URL: str = os.getenv("MP_PENDING_URL", "")
    MP_WEBHOOK_SECRET: str = os.getenv("MP_WEBHOOK_SECRET", "")

    # Mentor IA (API compatible con OpenAI: OpenAI, Groq, OpenRouter, Ollama...)
    # Por defecto apunta a Google Gemini (tier gratuito en AI Studio, sin tarjeta).
    # Modelos válidos: gemini-3.5-flash, gemini-3.6-flash, gemini-2.5-flash (retirado).
    # Para Groq usa https://api.groq.com/openai/v1 con groq/compound.
    # Para OpenRouter usa https://openrouter.ai/api/v1 con IDs tipo openai/gpt-4o-mini.
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gemini-3.5-flash")

    # Redis for real-time check-in notifications
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

settings = Settings()

# Fail-safe: en producción la SECRET_KEY debe ser un valor real (no el placeholder ni vacía),
# porque se usa para firmar los JWT. En desarrollo solo se advierte.
DEFAULT_SECRET_KEY = "your-secret-key-123-change-in-production"
if not settings.SECRET_KEY or settings.SECRET_KEY == DEFAULT_SECRET_KEY:
    if settings.ENVIRONMENT == "production":
        raise RuntimeError(
            "SECRET_KEY must be set in production! Define la variable de entorno SECRET_KEY "
            "con un valor aleatorio (p. ej. el resultado de: openssl rand -hex 32). "
            "NO uses el valor de ejemplo del .env.example."
        )
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