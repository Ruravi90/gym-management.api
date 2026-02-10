#!/usr/bin/env python3
"""
Debug script to test the statistics functions that are causing 500 errors
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_statistics_functions():
    """Test the specific functions that are causing 500 errors"""
    try:
        print("Testing statistics functions...")
        
        # Import necessary modules
        from app.database import SessionLocal
        from app import crud
        
        # Create a database session
        db = SessionLocal()
        
        try:
            print("\n1. Testing get_total_memberships_count...")
            total = crud.membership.get_total_memberships_count(db)
            print(f"   Total memberships: {total}")
            
            print("\n2. Testing get_active_memberships_count...")
            active = crud.membership.get_active_memberships_count(db)
            print(f"   Active memberships: {active}")
            
            print("\n3. Testing get_expired_memberships_count...")
            expired = crud.membership.get_expired_memberships_count(db)
            print(f"   Expired memberships: {expired}")
            
            print("\n4. Testing get_upcoming_expirations...")
            upcoming = crud.membership.get_upcoming_expirations(db, days=30)
            print(f"   Upcoming expirations: {len(upcoming)}")
            
            print("\n5. Testing the combined statistics function...")
            # Simulate what happens in the API
            total_memberships = crud.membership.get_total_memberships_count(db)
            active_memberships = crud.membership.get_active_memberships_count(db)
            expired_memberships = crud.membership.get_expired_memberships_count(db)
            upcoming_expirations = crud.membership.get_upcoming_expirations(db, days=30)
            
            result = {
                "total_memberships": total_memberships,
                "active_memberships": active_memberships,
                "expired_memberships": expired_memberships,
                "upcoming_expirations": len(upcoming_expirations),
                "upcoming_expirations_list": upcoming_expirations
            }
            
            print(f"   Combined result: {result}")
            
            print("\n✅ All statistics functions working correctly!")
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR in statistics functions: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            db.close()
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Test basic database connectivity"""
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            # Test a simple query
            from sqlalchemy import text
            result = db.execute(text("SELECT 1")).fetchone()
            print(f"✅ Database connection working: {result}")
            return True
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting debug test for statistics endpoint...")
    
    if test_database_connection():
        test_statistics_functions()
    else:
        print("Cannot proceed - database connection failed")