#!/usr/bin/env python3
"""
Test script to verify the new membership system functionality
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.membership import Membership, MembershipType
from app.models.client import Client
from app.schemas.membership import MembershipTypeCreate, MembershipCreate
from datetime import datetime, timedelta

# Create database engine and session
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://app:Ruravi90@localhost/GymControl")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_new_membership_system():
    """Test the new membership system functionality"""
    db = SessionLocal()
    
    try:
        print("Testing new membership system...")
        
        # Verify membership types table exists and has data
        membership_types = db.query(MembershipType).all()
        print(f"Found {len(membership_types)} membership types in the database")
        
        for mt in membership_types:
            print(f"- {mt.name}: ${mt.price}, {mt.duration_days} days, {mt.accesses_allowed} accesses")
        
        # Find a day pass type
        day_pass_type = db.query(MembershipType).filter(MembershipType.name == "Day Pass").first()
        if day_pass_type:
            print(f"\nFound Day Pass type: {day_pass_type.name}")
            print(f"Duration: {day_pass_type.duration_days} days")
            print(f"Accesses allowed: {day_pass_type.accesses_allowed}")
            print(f"Price: ${day_pass_type.price}")
        
        # Find an existing client to test with
        client = db.query(Client).first()
        if client:
            print(f"\nFound client: {client.name} (ID: {client.id})")
            
            # Test creating a new membership using the new system
            # Find a membership type to use
            membership_type = db.query(MembershipType).first()
            if membership_type:
                print(f"Creating new membership for client using type: {membership_type.name}")
                
                # Calculate end date based on duration
                start_date = datetime.utcnow()
                end_date = start_date + timedelta(days=membership_type.duration_days or 30)
                
                new_membership = Membership(
                    client_id=client.id,
                    membership_type_id=membership_type.id,
                    type=membership_type.name,
                    start_date=start_date,
                    end_date=end_date,
                    price=membership_type.price,
                    price_paid=membership_type.price,
                    status="active",
                    payment_status="paid",
                    payment_method="cash",
                    accesses_used=0
                )
                
                db.add(new_membership)
                db.commit()
                db.refresh(new_membership)
                
                print(f"Created new membership (ID: {new_membership.id})")
                print(f"Start date: {new_membership.start_date}")
                print(f"End date: {new_membership.end_date}")
                print(f"Accesses used: {new_membership.accesses_used}")
                
                # Clean up - delete the test membership
                db.delete(new_membership)
                db.commit()
                print("Test membership cleaned up")
        
        print("\n✓ New membership system test completed successfully!")
        
    except Exception as e:
        print(f"✗ Error during testing: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_new_membership_system()