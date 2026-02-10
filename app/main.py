import app.utils.bcrypt_compat  # noqa: F401 — must be imported first for passlib/bcrypt compatibility


from fastapi import FastAPI, Depends, HTTPException, Request
from app.config import settings
from app.utils.logging import setup_logging
import asyncio
from aerich import Command

# Initialize logging
logger = setup_logging()

from app.api import users, memberships, attendance, membership_types, gym_class
from app.api.clients import router as clients_router
from app.api.facial_recognition import router as facial_recognition_router
from app.api.auth import router as auth_router
from app.middleware.security import add_security_middleware, limiter, common_limits, auth_limits, file_upload_limits

# Configure FastAPI app with metadata
app = FastAPI(
    title="Gym Management System API",
    description="API for managing gym memberships, attendance, and facial recognition",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# Add security middleware
add_security_middleware(app)

from fastapi.middleware.cors import CORSMiddleware

# Configure CORS based on environment
if settings.FRONTEND_URL == "*":
    allow_origins = ["*"]
else:
    allow_origins = [origin.strip() for origin in settings.FRONTEND_URL.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Allow credentials to be sent with cross-origin requests
)

# Apply rate limiting to specific routes
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(clients_router, prefix="/clients", tags=["clients"])
app.include_router(memberships.router, prefix="/memberships", tags=["memberships"])
app.include_router(membership_types.router, prefix="/membership-types", tags=["membership-types"])
app.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
app.include_router(gym_class.router, prefix="/classes", tags=["classes"])
app.include_router(facial_recognition_router, prefix="/facial-recognition", tags=["facial-recognition"])

from tortoise.contrib.fastapi import register_tortoise
from app.config import TORTOISE_CONFIG

# Register Tortoise ORM with FastAPI
register_tortoise(
    app,
    config=TORTOISE_CONFIG,
    generate_schemas=True,  # Automatically generate schema
    add_exception_handlers=True,
)

# Global flag to ensure seeders run only once
import threading
seeder_lock = threading.Lock()
seeders_executed = False

# Startup event to run seeders after database is initialized
@app.on_event("startup")
async def startup_event():
    global seeders_executed
    with seeder_lock:
        if seeders_executed:
            return
        seeders_executed = True
    
    logger.info("✅ Database schema initialized at startup via Tortoise ORM")

    # Run migrations using Aerich
    try:
        command = Command(tortoise_config=TORTOISE_CONFIG, app="models")
        await command.init()
        await command.upgrade(run_in_transaction=True)
        logger.info("✅ Migrations applied successfully")
    except Exception as e:
        logger.error(f"❌ Error applying migrations: {str(e)}")

    # Import and run seeders after database initialization
    try:
        from app.seeders.seed_data import seed_super_admin, seed_membership_types
        logger.info("🌱 Starting database seeding process...")

        # Run individual seeders
        await seed_super_admin()
        await seed_membership_types()

        logger.info("✅ Database seeding completed at startup!")
    except Exception as e:
        logger.warning(f"⚠️  Warning: Could not run seeders: {str(e)}")
        logger.info("💡 This may be due to database connection timing. Server will continue to start.")
        logger.exception("Seeder failure details:")

@app.get("/")
@limiter.limit(common_limits)
def read_root(request: Request):
    return {"message": "Welcome to Gym Management System API", "environment": settings.ENVIRONMENT}


@app.get("/health")
@limiter.limit(common_limits)
def health_check(request: Request):
    return {"status": "ok", "environment": settings.ENVIRONMENT}