import requests

# Test the NEW API endpoints to verify they work correctly
BASE_URL = "http://localhost:8000"

def test_api_routes():
    # Test the NEW types endpoint at /membership-types
    try:
        # This requires authentication, so we'll expect a 401 or 403
        # But we want to make sure it doesn't give a 422 error
        headers = {
            "Authorization": "Bearer invalid_token_for_testing",
            "Content-Type": "application/json"
        }
        
        # Test the NEW endpoint
        response = requests.get(f"{BASE_URL}/membership-types", headers=headers)
        print(f"GET /membership-types - Status: {response.status_code}")
        
        if response.status_code == 422:
            print("❌ ERROR: Still getting 422 Unprocessable Entity on /membership-types")
            print(f"Response: {response.text}")
        elif response.status_code in [401, 403]:
            print("✅ SUCCESS: Getting expected auth error on /membership-types (not 422)")
        else:
            print(f"❓ UNEXPECTED: Got status {response.status_code} on /membership-types")
            
        # Also test the original memberships endpoint to make sure it still works
        response2 = requests.get(f"{BASE_URL}/memberships", headers=headers)
        print(f"GET /memberships - Status: {response2.status_code}")
        
        if response2.status_code == 422:
            print("❌ ERROR: Getting 422 Unprocessable Entity on /memberships")
        elif response2.status_code in [401, 403]:
            print("✅ SUCCESS: Getting expected auth error on /memberships (not 422)")
        else:
            print(f"❓ UNEXPECTED: Got status {response2.status_code} on /memberships")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server. Is it running?")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_api_routes()