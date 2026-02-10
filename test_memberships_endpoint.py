import requests

# Test the specific memberships endpoint that is failing
BASE_URL = "http://localhost:8000"

def test_memberships_endpoint():
    print("Testing the specific memberships endpoint that is failing...")
    
    try:
        print("\n1. Testing /memberships endpoint:")
        response = requests.get(f"{BASE_URL}/memberships")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200] if response.text else 'No content'}...")
        
        print("\n2. Testing with basic headers to simulate browser request:")
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        response2 = requests.get(f"{BASE_URL}/memberships", headers=headers)
        print(f"   Status: {response2.status_code}")
        print(f"   Response: {response2.text[:200] if response2.text else 'No content'}...")
        
        print("\n3. Testing other endpoints for comparison:")
        endpoints = [
            "/health",
            "/users",
            "/clients",
            "/attendance"
        ]
        
        for endpoint in endpoints:
            try:
                resp = requests.get(f"{BASE_URL}{endpoint}")
                print(f"   {endpoint}: {resp.status_code}")
            except:
                print(f"   {endpoint}: FAILED TO CONNECT")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {str(e)}")
        print("This could indicate a server-side error in the /memberships endpoint")
    except Exception as e:
        print(f"❌ GENERAL ERROR: {str(e)}")

if __name__ == "__main__":
    test_memberships_endpoint()