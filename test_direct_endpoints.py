import requests

# Test the specific endpoints that are failing
BASE_URL = "http://localhost:8000"

def test_specific_endpoints():
    print("Testing specific endpoints that are failing...")
    
    # Test without authentication first to see if the route exists
    try:
        print("\n1. Testing /health endpoint (should work without auth):")
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Health endpoint - Status: {response.status_code}")
        
        print("\n2. Testing /memberships/statistics endpoint (will fail without auth):")
        response = requests.get(f"{BASE_URL}/memberships/statistics")
        print(f"   Statistics endpoint - Status: {response.status_code}")
        
        print("\n3. Testing /memberships endpoint (will fail without auth):")
        response = requests.get(f"{BASE_URL}/memberships")
        print(f"   Memberships endpoint - Status: {response.status_code}")
        
        print("\n4. Testing /membership-types endpoint (will fail without auth):")
        response = requests.get(f"{BASE_URL}/membership-types")
        print(f"   Membership types endpoint - Status: {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server. Server may not be running or is not accessible.")
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {str(e)}")
    except Exception as e:
        print(f"❌ GENERAL ERROR: {str(e)}")

if __name__ == "__main__":
    test_specific_endpoints()