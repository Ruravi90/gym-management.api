"""
Dummy database dependency for FastAPI compatibility.
This is a placeholder for SQLAlchemy Session that is no longer used.
All database operations now use Tortoise ORM directly.
"""

async def get_db():
    """Dummy async generator for database session compatibility."""
    yield None
