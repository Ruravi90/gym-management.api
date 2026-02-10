#!/usr/bin/env python3
"""
Simple seeder script for initial data
"""
import bcrypt

# Fix for passlib compatibility with bcrypt 4.0+
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("About", (object,), {"__version__": bcrypt.__version__})

# Fix for ValueError: password cannot be longer than 72 bytes
_original_hashpw = bcrypt.hashpw
def _patched_hashpw(password, salt):
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = password
    # Bcrypt algorithm maximum password length is 72 bytes
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return _original_hashpw(password_bytes, salt)

bcrypt.hashpw = _patched_hashpw

import asyncio
import sys
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.config import TORTOISE_CONFIG
from tortoise import Tortoise


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


async def init_db():
    """Initialize Tortoise ORM"""
    await Tortoise.init(config=TORTOISE_CONFIG)
    # Generate schemas to ensure tables exist
    await Tortoise.generate_schemas()


async def seed_super_admin():
    """Seed the database with a super admin user."""
    print("Seeding super admin...")

    # Import models inside the function to ensure they're available after DB initialization
    from app.models.user import User, UserRoleEnum

    # Check if super admin already exists
    existing_admin = await User.filter(email="ruravi@icloud.com").first()
    if not existing_admin:
        # Create super admin user
        super_admin = await User.create(
            name="Ruravi Aguilar",
            email="ruravi@icloud.com",
            phone="3317242995",
            role=UserRoleEnum.SUPER_ADMIN,
            hashed_password=hash_password("SecurePass123"),  # Use a strong default password
            status=True
        )

        print(f"Super admin user created with ID: {super_admin.id}")

    existing_admin = await User.filter(email="oscar@pantherwarriors.com").first()
    if not existing_admin:
        # Create super admin user
        admin = await User.create(
            name="Oscar Panther",
            email="oscar@pantherwarriors.com",
            phone="3317242995",
            role=UserRoleEnum.ADMIN,
            hashed_password=hash_password("Oscar2025"),  # Use a strong default password
            status=True
        )

        print(f"Admin user created with ID: {admin.id}")


async def seed_membership_types():
    """Seed the database with default membership types."""
    print("Seeding membership types...")

    from app.models.membership import MembershipType

    # Define default membership types with their characteristics
    default_memberships = [
        {
            "name": "Day Pass",
            "duration_days": 1,
            "accesses_allowed": 1,
            "price": 25.00,
            "description": "One-day unlimited access",
            "is_active": True
        },
        {
            "name": "Weekly Pass",
            "duration_days": 7,
            "accesses_allowed": None,  # Unlimited access
            "price": 40.00,
            "description": "Seven-day unlimited access",
            "is_active": True
        },
        {
            "name": "5-Punch Pass",
            "duration_days": 30,
            "accesses_allowed": 5,
            "price": 100.00,
            "description": "Five visits within 30 days",
            "is_active": True
        },
        {
            "name": "10-Punch Pass",
            "duration_days": 60,
            "accesses_allowed": 10,
            "price": 180.00,
            "description": "Ten visits within 60 days",
            "is_active": True
        },
        {
            "name": "Monthly Basic",
            "duration_days": 30,
            "accesses_allowed": None,  # Unlimited access
            "price": 55.00,
            "description": "Standard monthly membership",
            "is_active": True
        },
        {
            "name": "Monthly Premium",
            "duration_days": 30,
            "accesses_allowed": None,  # Unlimited access
            "price": 85.00,
            "description": "Premium monthly membership with additional perks",
            "is_active": True
        },
        {
            "name": "Annual Membership",
            "duration_days": 365,
            "accesses_allowed": None,  # Unlimited access
            "price": 750.00,
            "description": "Yearly membership with discount",
            "is_active": True
        },
        {
            "name": "Student Monthly",
            "duration_days": 30,
            "accesses_allowed": None,  # Unlimited access
            "price": 35.00,
            "description": "Discounted monthly membership for students",
            "is_active": True
        },
        {
            "name": "Family Monthly",
            "duration_days": 30,
            "accesses_allowed": None,  # Unlimited access
            "price": 140.00,
            "description": "Monthly membership for up to 4 family members",
            "is_active": True
        }
    ]

    print("Seeding default membership types...")
    for membership_data in default_memberships:
        # Check if membership type already exists
        existing_type = await MembershipType.filter(name=membership_data['name']).first()
        if existing_type:
            print(f"Membership type '{membership_data['name']}' already exists, skipping.")
            continue

        membership_type = await MembershipType.create(**membership_data)
        print(f"Created membership type: {membership_type.name}")

    print(f"Seeded {len(default_memberships)} membership types")


async def seed_sample_clients():
    """Seed the database with sample clients."""
    print("Seeding sample clients...")
    
    from app.models.client import Client

    sample_clients = [
        {
            "name": "Juan Pérez",
            "email": "juan.perez@example.com",
            "phone": "3312345678",
            "membership_type": "basic",
            "status": True
        },
        {
            "name": "María García",
            "email": "maria.garcia@example.com",
            "phone": "3323456789",
            "membership_type": "premium",
            "status": True
        },
        {
            "name": "Carlos López",
            "email": "carlos.lopez@example.com",
            "phone": "3334567890",
            "membership_type": "VIP",
            "status": True
        },
        {
            "name": "Ana Martínez",
            "email": "ana.martinez@example.com",
            "phone": "3345678901",
            "membership_type": "student",
            "status": True
        },
        {
            "name": "Roberto Sánchez",
            "email": "roberto.sanchez@example.com",
            "phone": "3356789012",
            "membership_type": "family",
            "status": True
        }
    ]

    for client_data in sample_clients:
        # Check if client already exists
        existing_client = await Client.filter(email=client_data['email']).first()
        if existing_client:
            print(f"Client '{client_data['name']}' already exists, skipping.")
            continue

        client = await Client.create(**client_data)
        print(f"Created client: {client.name}")

    print(f"Seeded {len(sample_clients)} sample clients")


async def run_seeders():
    """Run all seeders to populate the database with initial data."""
    try:
        print("Starting database seeding process...")

        # Seed super admin first
        await seed_super_admin()

        # Seed membership types
        await seed_membership_types()

        print("Database seeding completed successfully!")

    except Exception as e:
        print(f"Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Running seeders...")
    asyncio.run(run_seeders())
    print("Seeders completed!")