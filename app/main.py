from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app import models
from app.config import settings

from app.api import users, memberships, attendance
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
app.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
app.include_router(facial_recognition_router, prefix="/facial-recognition", tags=["facial-recognition"])

@app.get("/")
@limiter.limit(common_limits)
def read_root(request: Request):
    return {"message": "Welcome to Gym Management System API", "environment": settings.ENVIRONMENT}

@app.get("/health")
@limiter.limit(common_limits)
def health_check(request: Request, db: Session = Depends(get_db)):
    return {"status": "ok", "environment": settings.ENVIRONMENT}

# Add a startup event to initialize the database if needed
@app.on_event("startup")
def startup_event():
    try:
        # Create database tables if they don't exist
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Database connection error during startup: {e}")
        print("Application will continue running but database features may not be available.")

    # Run Alembic migrations automatically on startup
    try:
        from alembic.config import Config
        from alembic import command
        from pathlib import Path

        base_dir = Path(__file__).resolve().parents[1]
        alembic_ini = base_dir / "alembic.ini"
        if alembic_ini.exists():
            alembic_cfg = Config(str(alembic_ini))
            # Ensure alembic uses the runtime DB URL
            alembic_cfg.set_main_option('sqlalchemy.url', str(settings.DATABASE_URL))
            # Use 'heads' to allow applying when multiple branch heads exist.
            # Note: if migrations truly diverged you may need to create a merge
            # revision (alembic merge) to resolve branches.
            command.upgrade(alembic_cfg, 'heads')
            print("Alembic migrations applied successfully (target: heads).")
        else:
            print(f"alembic.ini not found at {alembic_ini}; skipping migrations.")
        
        # Importar y ejecutar los seeders para inicializar datos
        from app.seeders.run_seeders import run_seeders
        run_seeders()

        print("Database tables created and seeders executed successfully!")    
        
    except Exception as me:
        print(f"Failed to run Alembic migrations at startup: {me}")