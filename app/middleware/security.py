from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, FastAPI
from app.config import settings

# Initialize the limiter with storage URL if available, otherwise in-memory
limiter = Limiter(key_func=get_remote_address)

def add_security_middleware(app: FastAPI):
    """Add security middleware to the FastAPI application."""
    # Add rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Add ProxyHeadersMiddleware to trust X-Forwarded-Proto (fixes Mixed Content redirects)
    from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
    
    # Add custom security headers
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        # Add security headers to all responses
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        return response

# Define rate limits for different endpoints
common_limits = "200 per hour"
auth_limits = "10 per minute"
file_upload_limits = "5 per minute"