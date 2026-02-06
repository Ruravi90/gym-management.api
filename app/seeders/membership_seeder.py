from sqlalchemy.orm import Session
from app.models.membership import Membership
from app.models.client import Client
from app.utils.auth import hash_password
from datetime import datetime, timedelta

def seed_memberships(db: Session):
    """Seed the database with default membership templates (for reference, not tied to specific clients)."""

    # Check if membership templates already exist to avoid duplicates
    # We'll identify template memberships by checking if they're assigned to clients with names like "Cliente Basic 1"
    existing_template_memberships = db.query(Membership).join(Client).filter(Client.name.like("Cliente %")).count()
    
    if existing_template_memberships > 0:
        print("Membership templates already exist, skipping seeding.")
        return

    # Define default membership types with their characteristics
    default_memberships = [
        {
            "type": "basic",
            "price": 50.00,
            "duration_days": 30,
            "description": "Membresía básica con acceso limitado"
        },
        {
            "type": "premium",
            "price": 80.00,
            "duration_days": 30,
            "description": "Membresía premium con acceso ilimitado"
        },
        {
            "type": "VIP",
            "price": 120.00,
            "duration_days": 30,
            "description": "Membresía VIP con beneficios exclusivos"
        },
        {
            "type": "student",
            "price": 35.00,
            "duration_days": 30,
            "description": "Membresía estudiantil con descuento"
        },
        {
            "type": "family",
            "price": 150.00,
            "duration_days": 30,
            "description": "Membresía familiar para hasta 4 personas"
        }
    ]

    print("Seeding default membership templates...")
    for i, membership_data in enumerate(default_memberships):
        # Create sample clients for each membership type
        client = Client(
            name=f"Cliente {membership_data['type'].title()} {i+1}",
            email=f"{membership_data['type']}_{i+1}@example.com",
            phone=f"123456789{i+1}",
            membership_type=membership_data['type'],
            status=True
        )
        db.add(client)
        db.commit()
        db.refresh(client)

        # Calculate start and end dates for active membership
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=membership_data['duration_days'])

        # Create membership record
        membership = Membership(
            client_id=client.id,
            type=membership_data['type'],
            start_date=start_date,
            end_date=end_date,
            price=membership_data['price'],
            status="active",  # Changed from "available" to "active"
            payment_status="paid",  # Changed from "pending" to "paid" for demo purposes
            payment_method="cash",  # Added payment method
            notes=membership_data['description']
        )
        db.add(membership)

    db.commit()
    print(f"Seeded {len(default_memberships)} membership templates with associated clients.")