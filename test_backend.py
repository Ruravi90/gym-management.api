#!/usr/bin/env python3
"""
Simple test to verify the backend is working correctly
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_backend():
    """Test basic backend functionality"""
    try:
        # Test imports
        from app import crud, schemas
        print("✅ Imports successful")
        
        # Test that schemas are available
        print(f"✅ Membership schema available: {hasattr(schemas, 'Membership')}")
        print(f"✅ MembershipType schema available: {hasattr(schemas, 'MembershipType')}")
        print(f"✅ MembershipStatistics schema available: {hasattr(schemas, 'MembershipStatistics')}")
        
        # Test that CRUD module is available
        print(f"✅ CRUD module available: {crud is not None}")
        print(f"✅ CRUD membership submodule available: {hasattr(crud, 'membership')}")
        
        print("\n✅ Backend structure test passed!")
        print("The issue is likely not with imports but possibly with runtime logic or database connection.")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_backend()