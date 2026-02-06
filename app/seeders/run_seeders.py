from sqlalchemy.orm import Session
from app.seeders.membership_seeder import seed_memberships
from app.seeders.super_admin_seeder import seed_super_admin
from app.seeders.client_seeder import seed_sample_clients
from app.database import SessionLocal

def run_seeders():
    """Run all seeders to populate the database with initial data."""
    db = SessionLocal()
    try:
        print("Starting database seeding process...")

        # Seed super admin first
        seed_super_admin(db)

        # Seed sample clients (with their active memberships)
        #seed_sample_clients(db)

        # Only seed default membership templates if needed (these are separate from client memberships)
        #seed_memberships(db)

        print("Database seeding completed successfully!")

    except Exception as e:
        print(f"Error during seeding: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_seeders()