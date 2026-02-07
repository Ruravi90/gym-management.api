from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import the database configuration and models
import sys
import os
# Ensure project root is on sys.path so we can import the `app` package
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

# Prefer importing the application package modules so Alembic runs in the
# same module layout as the application (imports like `app.database`).
try:
    from app.database import Base
    # Import all models to ensure they are registered with the Base metadata
    # Add any new model modules here so Alembic sees their metadata.
    from app.models import user, attendance, membership, facial_encoding, gym_class, client
except Exception:
    # Fallback for environments where `app` package cannot be imported; try local imports
    from database import Base
    from models import user, attendance, membership, facial_encoding, gym_class, client

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use the metadata from the models
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Get database URL from environment variable or use default
    import os

    # First try to get from environment variable
    database_url = os.getenv("DATABASE_URL")

    # If not found in environment, try to read from config or use default
    if not database_url:
        # Try to read from config file or use default from alembic.ini
        database_url = config.get_main_option("sqlalchemy.url")

    # If still not found, use a default
    if not database_url:
        database_url = "mysql+pymysql://app:Ruravi90@localhost/GymControl"

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=database_url
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
