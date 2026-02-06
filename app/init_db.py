"""
Database initialization script for Railway deployment.
This script ensures the database is properly set up when the app starts.
"""
from database import engine, Base
from config import settings
import logging

def init_database():
    """Initialize the database tables."""
    try:
        # Create all tables defined in the models
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_database()