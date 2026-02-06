from sqlalchemy.orm import Session
from app.models.client import Client
from app.models.membership import Membership
from app.utils.auth import hash_password
from datetime import datetime, timedelta

def seed_sample_clients(db: Session):
    """Seed the database with sample clients."""

    # Check if clients already exist to avoid duplicates
    existing_clients = db.query(Client).count()
    if existing_clients > 0:
        print("Sample clients already exist, skipping seeding.")
        return

    # Define sample clients
    sample_clients = [
        {
            "name": "Ana García",
            "email": "ana.garcia@example.com",
            "phone": "3317242996",
            "membership_type": "premium"
        },
        {
            "name": "Carlos López",
            "email": "carlos.lopez@example.com",
            "phone": "3317242997",
            "membership_type": "VIP"
        },
        {
            "name": "María Rodríguez",
            "email": "maria.rodriguez@example.com",
            "phone": "3317242998",
            "membership_type": "basic"
        },
        {
            "name": "José Martínez",
            "email": "jose.martinez@example.com",
            "phone": "3317242999",
            "membership_type": "student"
        },
        {
            "name": "Laura Sánchez",
            "email": "laura.sanchez@example.com",
            "phone": "3317243000",
            "membership_type": "family"
        }
    ]

    print("Seeding sample clients...")
    for client_data in sample_clients:
        client = Client(
            name=client_data['name'],
            email=client_data['email'],
            phone=client_data['phone'],
            membership_type=client_data['membership_type'],
            status=True
        )
        db.add(client)
        db.commit()
        db.refresh(client)

        # Create an active membership for each client
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)  # 30-day membership
        
        membership = Membership(
            client_id=client.id,
            type=client_data['membership_type'],
            start_date=start_date,
            end_date=end_date,
            price=50.00,  # Default price
            status="active",
            payment_status="paid",
            payment_method="cash",
            notes=f"Membresía {client_data['membership_type']} activa"
        )
        db.add(membership)

    db.commit()
    print(f"Seeded {len(sample_clients)} sample clients with active memberships.")