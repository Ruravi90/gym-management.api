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
# Facial recognition disabled — replaced by QR-based check-in
# from app.api.facial_recognition import router as facial_recognition_router
from app.api.auth import router as auth_router
from app.api.audit_logs import router as audit_logs_router
from app.api.analytics import router as analytics_router
from app.api.payments import router as payments_router
from app.api.exercises import router as exercises_router
from app.api.routines import router as routines_router
from app.api.mentor import router as mentor_router
from app.api.measurements import router as measurements_router
from app.api.tenants import router as tenants_router
from app.api.webhooks import router as webhooks_router
from app.api.billing import router as billing_router
from app.middleware.security import add_security_middleware, limiter, common_limits, auth_limits, file_upload_limits
from app.services.checkin_notifier import init_redis, close_redis

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
# NOTE: allow_credentials=True requires explicit origins (not "*")
if settings.FRONTEND_URL == "*":
    # In dev, reflect the Origin header. FastAPI's CORSMiddleware
    # handles this when allow_origins contains the actual requesting origin.
    allow_origins = ["*"]
else:
    allow_origins = [origin.strip() for origin in settings.FRONTEND_URL.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Apply rate limiting to specific routes
logger.info("Including auth router...")
app.include_router(auth_router, prefix="/auth", tags=["auth"])
logger.info("Including users router...")
app.include_router(users.router, prefix="/users", tags=["users"])
logger.info("Including clients router...")
app.include_router(clients_router, prefix="/clients", tags=["clients"])
logger.info("Including memberships router...")
app.include_router(memberships.router, prefix="/memberships", tags=["memberships"])
logger.info("Including membership-types router...")
app.include_router(membership_types.router, prefix="/membership-types", tags=["membership-types"])
logger.info("Including attendance router...")
app.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
logger.info("Including classes router...")
app.include_router(gym_class.router, prefix="/classes", tags=["classes"])
# logger.info("Including facial-recognition router...")
# app.include_router(facial_recognition_router, prefix="/facial-recognition", tags=["facial-recognition"])
logger.info("Including audit-logs router...")
app.include_router(audit_logs_router, prefix="/audit-logs", tags=["audit-logs"])
app.include_router(payments_router, prefix="/payments", tags=["payments"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
from app.api.member import router as member_router
app.include_router(member_router, prefix="/member", tags=["member"])
from app.api.kaizen import router as kaizen_router
app.include_router(kaizen_router, prefix="/kaizen", tags=["kaizen"])
from app.api.gamification import router as gamification_router
app.include_router(gamification_router, prefix="/gamification", tags=["gamification"])
logger.info("Including exercises router...")
app.include_router(exercises_router, prefix="/exercises", tags=["exercises"])
logger.info("Including routines router...")
app.include_router(routines_router, prefix="/routines", tags=["routines"])
logger.info("Including mentor router...")
app.include_router(mentor_router, prefix="/mentor", tags=["mentor"])
logger.info("Including measurements router...")
app.include_router(measurements_router, prefix="/measurements", tags=["measurements"])
logger.info("Including tenants router...")
app.include_router(tenants_router, prefix="/tenants", tags=["tenants"])
app.include_router(webhooks_router, prefix="/webhooks", tags=["webhooks"])
app.include_router(billing_router, prefix="/billing", tags=["billing"])
logger.info("All routers included successfully")

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

    await init_redis()

    with seeder_lock:
        if seeders_executed:
            return
        seeders_executed = True
    
    logger.info("✅ Database schema initialized at startup via Tortoise ORM")

    # Run migrations using Aerich
    try:
        from tortoise import Tortoise
        conn = Tortoise.get_connection("default")
        
        # Manual emergency fix for missing columns
        logger.info("🛠️  Checking/Applying manual column fixes...")

        # Tenant table
        try:
            await conn.execute_query(
                "CREATE TABLE IF NOT EXISTS `tenants` ("
                "`id` INT AUTO_INCREMENT PRIMARY KEY,"
                "`name` VARCHAR(150) NOT NULL,"
                "`slug` VARCHAR(50) NOT NULL UNIQUE,"
                "`email` VARCHAR(100),"
                "`phone` VARCHAR(20),"
                "`address` LONGTEXT,"
                "`logo_url` VARCHAR(500),"
                "`status` VARCHAR(20) NOT NULL DEFAULT 'active',"
                "`max_users` INT NOT NULL DEFAULT 10,"
                "`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                "`updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
                ")"
            )
            logger.info("✅ Created tenants table")
        except: pass

        # tenant_id columns for all models
        tenant_columns = [
            ("users", "tenant_id", "INT"),
            ("clients", "tenant_id", "INT"),
            ("membership_types", "tenant_id", "INT"),
            ("memberships", "tenant_id", "INT"),
            ("attendance", "tenant_id", "INT"),
            ("audit_logs", "tenant_id", "INT"),
            ("exercises", "tenant_id", "INT"),
            ("routines", "tenant_id", "INT"),
            ("workout_sessions", "tenant_id", "INT"),
            ("body_measurements", "tenant_id", "INT"),
            ("kaizen_habits", "tenant_id", "INT"),
            ("kaizen_medals", "tenant_id", "INT"),
            ("xp_logs", "tenant_id", "INT"),
            ("weekly_challenges", "tenant_id", "INT"),
            ("classes", "tenant_id", "INT"),
            ("mentor_messages", "tenant_id", "INT"),
        ]
        for table, column, col_type in tenant_columns:
            try:
                await conn.execute_query(f"ALTER TABLE `{table}` ADD COLUMN `{column}` {col_type}")
                logger.info(f"✅ Added {column} to {table}")
            except: pass

        for column, col_type in [("waha_session", "VARCHAR(100) NULL"), ("waha_enabled", "BOOLEAN NOT NULL DEFAULT FALSE")]:
            try:
                await conn.execute_query(f"ALTER TABLE `tenants` ADD COLUMN `{column}` {col_type}")
            except: pass

        try:
            await conn.execute_query("ALTER TABLE `kaizen_habits` ADD COLUMN `reflection` LONGTEXT")
            logger.info("✅ Added reflection to kaizen_habits")
        except: pass
        try:
            await conn.execute_query("ALTER TABLE `kaizen_habits` ADD COLUMN `goal` LONGTEXT")
            logger.info("✅ Added goal to kaizen_habits")
        except: pass
        try:
            await conn.execute_query("ALTER TABLE `kaizen_logs` ADD COLUMN `reflection` LONGTEXT")
            logger.info("✅ Added reflection to kaizen_logs")
        except: pass
        try:
            await conn.execute_query("ALTER TABLE `users` ADD COLUMN `body_type` VARCHAR(20)")
            logger.info("✅ Added body_type to users")
        except: pass
        try:
            await conn.execute_query("ALTER TABLE `users` ADD COLUMN `height_cm` DOUBLE")
            logger.info("✅ Added height_cm to users")
        except: pass
        try:
            await conn.execute_query("ALTER TABLE `users` ADD COLUMN `age` INT")
            logger.info("✅ Added age to users")
        except: pass
        try:
            await conn.execute_query("ALTER TABLE `users` ADD COLUMN `sex` VARCHAR(10)")
            logger.info("✅ Added sex to users")
        except: pass
        try:
            await conn.execute_query("ALTER TABLE `users` ADD COLUMN `daily_activity` VARCHAR(20)")
            logger.info("✅ Added daily_activity to users")
        except: pass
        try:
            await conn.execute_query("ALTER TABLE `users` ADD COLUMN `injuries` LONGTEXT")
            logger.info("✅ Added injuries to users")
        except: pass
        try:
            await conn.execute_query("ALTER TABLE `users` ADD COLUMN `password_setup_at` DATETIME NULL")
            logger.info("✅ Added password_setup_at to users")
        except: pass
        for column, col_type in [("password_reset_token_hash", "VARCHAR(128) NULL"), ("password_reset_expires_at", "DATETIME NULL")]:
            try:
                await conn.execute_query(f"ALTER TABLE `users` ADD COLUMN `{column}` {col_type}")
                logger.info(f"✅ Added {column} to users")
            except: pass

        # Client report rate-limit columns
        try:
            await conn.execute_query("ALTER TABLE `clients` ADD COLUMN `last_weekly_checkin_at` DATETIME NULL")
            logger.info("✅ Added last_weekly_checkin_at to clients")
        except: pass
        try:
            await conn.execute_query("ALTER TABLE `clients` ADD COLUMN `last_monthly_report_at` DATETIME NULL")
            logger.info("✅ Added last_monthly_report_at to clients")
        except: pass

        # Gamification columns
        try:
            await conn.execute_query("ALTER TABLE `clients` ADD COLUMN `xp` INT DEFAULT 0")
            logger.info("✅ Added xp to clients")
        except: pass
        try:
            await conn.execute_query("ALTER TABLE `clients` ADD COLUMN `level` INT DEFAULT 1")
            logger.info("✅ Added level to clients")
        except: pass
        try:
            await conn.execute_query("ALTER TABLE `clients` ADD COLUMN `current_streak` INT DEFAULT 0")
            logger.info("✅ Added current_streak to clients")
        except: pass
        try:
            await conn.execute_query("ALTER TABLE `clients` ADD COLUMN `longest_streak` INT DEFAULT 0")
            logger.info("✅ Added longest_streak to clients")
        except: pass
        try:
            await conn.execute_query("ALTER TABLE `clients` ADD COLUMN `last_activity_date` DATE NULL")
            logger.info("✅ Added last_activity_date to clients")
        except: pass

        # Exercise GIF + detail columns
        try:
            await conn.execute_query("ALTER TABLE `exercises` ADD COLUMN `gif_urls` JSON NULL")
            logger.info("✅ Added gif_urls to exercises")
        except: pass
        try:
            await conn.execute_query("ALTER TABLE `exercises` ADD COLUMN `tips` TEXT NULL")
            logger.info("✅ Added tips to exercises")
        except: pass
        try:
            await conn.execute_query("ALTER TABLE `exercises` ADD COLUMN `common_mistakes` TEXT NULL")
            logger.info("✅ Added common_mistakes to exercises")
        except: pass
        try:
            await conn.execute_query("ALTER TABLE `exercises` ADD COLUMN `modifications` TEXT NULL")
            logger.info("✅ Added modifications to exercises")
        except: pass

        # Mentor messages history table
        try:
            await conn.execute_query(
                "CREATE TABLE IF NOT EXISTS `mentor_messages` ("
                "`id` INT AUTO_INCREMENT PRIMARY KEY,"
                "`client_id` INT NOT NULL,"
                "`role` VARCHAR(20) NOT NULL,"
                "`content` TEXT NOT NULL,"
                "`message_type` VARCHAR(30) NOT NULL,"
                "`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"
                ")"
            )
            logger.info("✅ Created mentor_messages table")
        except: pass

        command = Command(tortoise_config=TORTOISE_CONFIG, app="models")

        # 1) Fix old-format migrations FIRST (aerich 0.9.2 requires MODELS_STATE
        #    on the last migration file, otherwise init() raises).
        try:
            await command.fix_migrations()
        except Exception as e:
            logger.warning(f"⚠️  fix_migrations skipped: {e}")

        # 2) Initialize aerich (validates migration files format)
        try:
            await command.init()
        except Exception as e:
            logger.warning(f"⚠️  aerich init skipped: {e}")

        # 3) Apply pending migrations. If the schema already exists (created by
        #    Tortoise generate_schemas or manual ALTERs), this fails gracefully
        #    without blocking startup.
        try:
            await command.upgrade(run_in_transaction=True)
            logger.info("✅ Migrations applied successfully")
        except Exception as e:
            logger.warning(f"⚠️  Migrations not applied (schema may already be up to date): {e}")
    except Exception as e:
        logger.error(f"❌ Error during migration setup: {str(e)}")

    # Import and run seeders after database initialization
    try:
        from app.seeders.seed_data import seed_super_admin, seed_membership_types
        from app.seeders.seed_plans import seed_plans
        logger.info("🌱 Starting database seeding process...")

        # Run individual seeders
        await seed_super_admin()
        await seed_membership_types()
        await seed_plans()

        # Seed exercise catalog (routines feature)
        try:
            from app.seeders.seed_exercises import seed_exercises
            await seed_exercises()
        except Exception as e:
            logger.warning(f"⚠️  Warning: Could not seed exercises: {str(e)}")

        # Seed exercise GIFs from catalog
        try:
            from app.seeders.update_gifs import update_gifs
            await update_gifs()
        except Exception as e:
            logger.warning(f"⚠️  Warning: Could not seed exercise GIFs: {str(e)}")

        # Seed gamification achievements
        try:
            from app.seeders.seed_achievements import seed_achievements
            await seed_achievements()
        except Exception as e:
            logger.warning(f"⚠️  Warning: Could not seed achievements: {str(e)}")

        # Seed weekly challenges
        try:
            from app.seeders.seed_weekly_challenges import seed_weekly_challenges
            await seed_weekly_challenges()
        except Exception as e:
            logger.warning(f"⚠️  Warning: Could not seed weekly challenges: {str(e)}")

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


@app.on_event("shutdown")
async def shutdown_event():
    await close_redis()
