from sqlalchemy.orm import Session
from app.seeders.admin_seeder import seed_super_admin
from app.database import SessionLocal

def run_seeders():
    """Run all seeders to populate the database with initial data."""
    db = SessionLocal()
    try:
        print("Starting database seeding process...")

        # Seed super admin first
        print("About to seed super admin...")
        seed_super_admin(db)
        print("Super admin seeded successfully")

        print("Database seeding completed successfully!")

    except Exception as e:
        print(f"Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_seeders()