from sqlalchemy.orm import Session
from app.models.user import User
from app.models.user_role import UserRole
from app.utils.auth import hash_password

def seed_super_admin(db: Session):
    """Seed the database with a super admin user."""

    # Check if super admin already exists
    existing_admin = db.query(User).filter(User.email == "ruravi@icloud.com").first()
    if existing_admin:
        print("Super admin already exists, skipping seeding.")
        return

    # Create super admin user
    super_admin = User(
        name="Ruravi Aguilar",
        email="ruravi@icloud.com",
        phone="3317242995",
        role=UserRole.SUPER_ADMIN,  # Assign super admin role
        hashed_password=hash_password("SecurePass123"),  # Use a strong default password (under 72 chars)
        status=True
    )

    db.add(super_admin)
    db.commit()
    db.refresh(super_admin)

    print(f"Super admin user created with ID: {super_admin.id}")
    return super_admin